# Architecture Documentation

이 문서는 Django-Tuto 프로젝트에 적용된 클린 아키텍처(Clean Architecture), 클린 코드(Clean Code), DDD(Domain-Driven Design) 원칙을 설명합니다.

## 목차

1. [아키텍처 개요](#아키텍처-개요)
2. [레이어 구조](#레이어-구조)
3. [Shop 앱 상세 구조](#shop-앱-상세-구조)
4. [주요 개선사항](#주요-개선사항)
5. [코드 예제](#코드-예제)
6. [마이그레이션 가이드](#마이그레이션-가이드)

## 아키텍처 개요

### 적용된 원칙

#### 1. Clean Architecture
- **의존성 역전 원칙(Dependency Inversion)**: 고수준 모듈이 저수준 모듈에 의존하지 않고, 둘 다 추상화에 의존합니다.
- **레이어 분리**: Domain, Application, Infrastructure, Presentation 레이어로 분리하여 관심사를 명확히 구분합니다.
- **비즈니스 로직의 독립성**: 도메인 로직은 프레임워크, DB, UI에 독립적입니다.

#### 2. Domain-Driven Design (DDD)
- **Entities**: 고유 식별자를 가진 도메인 객체 (Product, Order, OrderItem)
- **Value Objects**: 불변 값 객체 (Money, OrderStatus, Quantity)
- **Domain Services**: 여러 엔티티에 걸친 비즈니스 로직 (OrderDomainService)
- **Repositories**: 도메인 객체의 컬렉션 인터페이스
- **Aggregates**: Order는 OrderItem의 Aggregate Root

#### 3. Clean Code
- **단일 책임 원칙(SRP)**: 각 클래스와 함수는 하나의 책임만 가집니다.
- **명확한 네이밍**: 의도를 명확히 드러내는 이름 사용
- **작은 함수**: 함수는 한 가지 일만 수행
- **불변성**: Value Objects는 불변 객체로 설계

## 레이어 구조

```
apps/shop/
├── domain/                    # 도메인 레이어 (비즈니스 로직의 핵심)
│   ├── entities.py           # 엔티티 (Product, Order, OrderItem)
│   ├── value_objects.py      # 값 객체 (Money, OrderStatus, Quantity)
│   ├── services.py           # 도메인 서비스
│   ├── repositories.py       # 저장소 인터페이스
│   └── exceptions.py         # 도메인 예외
├── application/              # 애플리케이션 레이어 (유스케이스)
│   ├── dto.py               # 데이터 전송 객체
│   └── use_cases.py         # 유스케이스 구현
├── infrastructure/           # 인프라 레이어 (기술 구현)
│   ├── orm_models.py        # Django ORM 모델
│   ├── repositories.py      # 저장소 구현체
│   └── mappers.py           # 도메인 ↔ ORM 변환
├── presentation/            # 프레젠테이션 레이어 (API)
│   ├── views.py            # API 뷰
│   └── serializers.py      # 시리얼라이저
├── models.py               # Django 호환성을 위한 모델 임포트
├── serializers.py          # Django 호환성을 위한 시리얼라이저 임포트
└── views.py                # Django 호환성을 위한 뷰 임포트
```

### 의존성 방향

```
Presentation → Application → Domain
Infrastructure → Domain
```

- **Domain**: 다른 레이어에 의존하지 않음 (순수 비즈니스 로직)
- **Application**: Domain에만 의존
- **Infrastructure**: Domain의 인터페이스 구현
- **Presentation**: Application과 Infrastructure 사용

## Shop 앱 상세 구조

### Domain Layer

#### 1. Value Objects (`domain/value_objects.py`)

**Money** - 금액을 표현하는 불변 객체
```python
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "KRW"

    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
```

**특징:**
- 불변 객체 (frozen=True)
- 비즈니스 규칙 캡슐화 (통화 검증, 음수 방지)
- 연산자 오버로딩으로 직관적인 사용

**OrderStatus** - 주문 상태를 표현하는 Enum
```python
class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        # 상태 전환 규칙 정의
```

**특징:**
- 상태 전환 규칙을 도메인 로직으로 캡슐화
- 잘못된 상태 전환 방지

**Quantity** - 수량을 표현하는 불변 객체
```python
@dataclass(frozen=True)
class Quantity:
    value: int

    def __sub__(self, other: 'Quantity') -> 'Quantity':
        result = self.value - other.value
        if result < 0:
            raise ValueError("Result quantity cannot be negative")
        return Quantity(result)
```

#### 2. Entities (`domain/entities.py`)

**Product** - 상품 엔티티
```python
@dataclass
class Product:
    id: Optional[int]
    name: str
    price: Money
    stock: Quantity

    def reserve_stock(self, quantity: Quantity) -> None:
        """재고 예약 (재고 차감)"""
        if not self.has_sufficient_stock(quantity):
            raise InsufficientStockError(...)
        self.stock = self.stock - quantity
```

**특징:**
- 재고 관리 로직을 엔티티 내부에 캡슐화
- 불변식(invariant) 보장

**Order** - 주문 엔티티 (Aggregate Root)
```python
@dataclass
class Order:
    id: Optional[int]
    user_id: int
    status: OrderStatus
    items: List[OrderItem]

    @property
    def total_amount(self) -> Money:
        """주문 총액 계산"""
        total = Money.zero()
        for item in self.items:
            total = total + item.line_total
        return total

    def change_status(self, new_status: OrderStatus) -> None:
        """주문 상태 변경"""
        if not self.status.can_transition_to(new_status):
            raise InvalidOrderStateError(...)
        self.status = new_status
```

**특징:**
- Aggregate Root로 OrderItem 관리
- 비즈니스 규칙 캡슐화 (상태 전환, 총액 계산)
- DB 저장 로직 없음 (순수 비즈니스 로직)

#### 3. Domain Services (`domain/services.py`)

**OrderDomainService** - 주문 도메인 서비스
```python
class OrderDomainService:
    @staticmethod
    def create_order_with_items(
        user_id: int,
        products_and_quantities: List[Tuple[Product, Quantity]]
    ) -> Order:
        """여러 엔티티에 걸친 주문 생성 로직"""
        # 재고 검증
        for product, quantity in products_and_quantities:
            if not product.has_sufficient_stock(quantity):
                raise InsufficientStockError(...)

        # 주문 아이템 생성
        order_items = [
            OrderItem.create_from_product(product, quantity)
            for product, quantity in products_and_quantities
        ]

        return Order.create(user_id=user_id, items=order_items)
```

**특징:**
- 여러 엔티티에 걸친 비즈니스 로직
- 트랜잭션 관리는 Application Layer에서 처리

#### 4. Repository Interfaces (`domain/repositories.py`)

```python
class ProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[Product]:
        pass

    @abstractmethod
    def save(self, product: Product) -> Product:
        pass
```

**특징:**
- 인터페이스만 정의 (구현은 Infrastructure Layer)
- 도메인 객체로만 작동 (ORM 모델 노출 안 함)

### Application Layer

#### Use Cases (`application/use_cases.py`)

**CreateOrderUseCase** - 주문 생성 유스케이스
```python
class CreateOrderUseCase:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository

    @transaction.atomic
    def execute(self, dto: CreateOrderDTO) -> OrderDTO:
        """주문 생성 및 재고 차감"""
        # 1. 상품 조회
        products = self.product_repository.find_by_ids(product_ids)

        # 2. 도메인 서비스로 주문 생성
        order = OrderDomainService.create_order_with_items(...)

        # 3. 재고 예약
        OrderDomainService.reserve_inventory_for_order(order, products)

        # 4. 저장
        for product in products:
            self.product_repository.save(product)

        saved_order = self.order_repository.save(order)

        return self._to_dto(saved_order)
```

**특징:**
- 단일 책임: 주문 생성 유스케이스만 처리
- 트랜잭션 관리 (@transaction.atomic)
- DTO를 통한 레이어 간 데이터 전송
- 의존성 주입을 통한 느슨한 결합

#### DTOs (`application/dto.py`)

```python
@dataclass
class CreateOrderDTO:
    """주문 생성 요청 DTO"""
    user_id: int
    items: List[OrderItemRequestDTO]

@dataclass
class OrderDTO:
    """주문 응답 DTO"""
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    items: List[OrderItemDTO]
    created_at: datetime
```

**특징:**
- 레이어 간 데이터 전송만 담당
- 비즈니스 로직 없음

### Infrastructure Layer

#### ORM Models (`infrastructure/orm_models.py`)

```python
class ProductORM(models.Model):
    """상품 ORM 모델"""
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "shop_product"
```

**특징:**
- Django ORM 모델 (DB 테이블 매핑)
- 비즈니스 로직 없음
- 도메인 엔티티와 분리

#### Mappers (`infrastructure/mappers.py`)

```python
class ProductMapper:
    @staticmethod
    def to_domain(orm_model: ProductORM) -> Product:
        """ORM 모델을 도메인 엔티티로 변환"""
        return Product(
            id=orm_model.id,
            name=orm_model.name,
            price=Money.from_decimal(orm_model.price),
            stock=Quantity(orm_model.stock),
        )

    @staticmethod
    def to_orm(domain_entity: Product, orm_model: ProductORM = None) -> ProductORM:
        """도메인 엔티티를 ORM 모델로 변환"""
        if orm_model is None:
            orm_model = ProductORM()

        orm_model.name = domain_entity.name
        orm_model.price = domain_entity.price.to_decimal()
        orm_model.stock = domain_entity.stock.value

        return orm_model
```

**특징:**
- 양방향 변환 제공
- 도메인과 인프라 계층 분리

#### Repository Implementations (`infrastructure/repositories.py`)

```python
class DjangoProductRepository(ProductRepository):
    """Django ORM 기반 상품 저장소 구현"""

    def find_by_id(self, product_id: int) -> Optional[Product]:
        try:
            orm_model = ProductORM.objects.get(id=product_id)
            return ProductMapper.to_domain(orm_model)
        except ProductORM.DoesNotExist:
            return None

    def save(self, product: Product) -> Product:
        if product.id:
            orm_model = ProductORM.objects.get(id=product.id)
            orm_model = ProductMapper.to_orm(product, orm_model)
        else:
            orm_model = ProductMapper.to_orm(product)

        orm_model.save()
        return ProductMapper.to_domain(orm_model)
```

**특징:**
- Repository 인터페이스 구현
- Mapper를 사용하여 도메인 객체 변환
- 데이터베이스 접근 로직 캡슐화

### Presentation Layer

#### Views (`presentation/views.py`)

```python
class OrderViewSet(viewsets.ViewSet):
    """주문 API ViewSet"""
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_repository = DjangoOrderRepository()
        self.product_repository = DjangoProductRepository()

    def create(self, request):
        """주문 생성"""
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            use_case = CreateOrderUseCase(
                self.order_repository,
                self.product_repository
            )
            order_dto = use_case.execute(serializer.to_dto(request.user.id))

            data = OrderSerializer.from_dto(order_dto)
            return Response(data, status=201)

        except InsufficientStockError as e:
            return Response({"error": str(e)}, status=400)
```

**특징:**
- Use Case를 통한 비즈니스 로직 실행
- HTTP 요청/응답 처리만 담당
- 에러 핸들링 및 상태 코드 관리

#### Serializers (`presentation/serializers.py`)

```python
class CreateOrderSerializer(serializers.Serializer):
    """주문 생성 요청 Serializer"""
    items = OrderItemRequestSerializer(many=True)

    def to_dto(self, user_id: int) -> CreateOrderDTO:
        """Serializer 데이터를 DTO로 변환"""
        items_dto = [
            OrderItemRequestDTO(
                product_id=item["product_id"],
                quantity=item["quantity"]
            )
            for item in self.validated_data["items"]
        ]

        return CreateOrderDTO(user_id=user_id, items=items_dto)
```

**특징:**
- 데이터 검증만 담당
- 비즈니스 로직 없음
- DTO 변환 메서드 제공

## 주요 개선사항

### 이전 코드의 문제점

#### 1. Serializer에 비즈니스 로직 혼재
```python
# 이전 (문제 있는 코드)
class OrderSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)

        total = 0
        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            price = product.price * quantity  # 비즈니스 로직!
            OrderItem.objects.create(...)
            total += price

        order.total_amount = total
        order.save()
        return order
```

**문제점:**
- 가격 계산 로직이 Serializer에 있음
- 재고 차감 없음
- 트랜잭션 없음
- 테스트 어려움

#### 2. View에 비즈니스 로직 혼재
```python
# 이전 (문제 있는 코드)
class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)  # 비즈니스 로직!
        return qs
```

**문제점:**
- 권한 로직이 View에 있음
- 재사용 불가능
- 테스트 어려움

### 개선된 코드

#### 1. 도메인 로직 분리
```python
# 개선된 코드
@dataclass
class OrderItem:
    @property
    def line_total(self) -> Money:
        """주문 라인 총액 계산"""
        return self.unit_price * self.quantity.value

@dataclass
class Order:
    @property
    def total_amount(self) -> Money:
        """주문 총액 계산"""
        total = Money.zero()
        for item in self.items:
            total = total + item.line_total
        return total
```

**장점:**
- 비즈니스 로직이 도메인 객체에 캡슐화
- 프레임워크 독립적
- 테스트 쉬움

#### 2. 재고 관리 로직 캡슐화
```python
# 개선된 코드
@dataclass
class Product:
    def reserve_stock(self, quantity: Quantity) -> None:
        """재고 예약 (재고 차감)"""
        if not self.has_sufficient_stock(quantity):
            raise InsufficientStockError(...)
        self.stock = self.stock - quantity

    def restore_stock(self, quantity: Quantity) -> None:
        """재고 복원 (주문 취소 시)"""
        self.stock = self.stock + quantity
```

**장점:**
- 재고 관리 로직이 Product 엔티티에 캡슐화
- 불변식 보장 (재고는 항상 0 이상)
- 주문 취소 시 재고 복원 가능

#### 3. 트랜잭션 관리
```python
# 개선된 코드
class CreateOrderUseCase:
    @transaction.atomic
    def execute(self, dto: CreateOrderDTO) -> OrderDTO:
        # 1. 상품 조회
        # 2. 주문 생성
        # 3. 재고 차감
        # 4. 저장
```

**장점:**
- 트랜잭션 경계 명확
- 롤백 보장
- 데이터 일관성 유지

#### 4. 상태 전환 규칙 캡슐화
```python
# 개선된 코드
class OrderStatus(Enum):
    def can_transition_to(self, new_status: 'OrderStatus') -> bool:
        allowed_transitions = {
            OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.PAID, OrderStatus.CANCELLED},
            # ...
        }
        return new_status in allowed_transitions.get(self, set())

@dataclass
class Order:
    def change_status(self, new_status: OrderStatus) -> None:
        if not self.status.can_transition_to(new_status):
            raise InvalidOrderStateError(...)
        self.status = new_status
```

**장점:**
- 상태 전환 규칙이 도메인 로직으로 캡슐화
- 잘못된 상태 전환 방지
- 비즈니스 규칙 명확

## 코드 예제

### 주문 생성 플로우

#### 1. API 요청
```http
POST /api/shop/orders/
Content-Type: application/json
Authorization: Bearer <token>

{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

#### 2. Presentation Layer (View)
```python
# presentation/views.py
def create(self, request):
    # 1. 데이터 검증
    serializer = CreateOrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    # 2. DTO 생성
    create_order_dto = serializer.to_dto(request.user.id)

    # 3. Use Case 실행
    use_case = CreateOrderUseCase(
        self.order_repository,
        self.product_repository
    )
    order_dto = use_case.execute(create_order_dto)

    # 4. 응답 반환
    data = OrderSerializer.from_dto(order_dto)
    return Response(data, status=201)
```

#### 3. Application Layer (Use Case)
```python
# application/use_cases.py
@transaction.atomic
def execute(self, dto: CreateOrderDTO) -> OrderDTO:
    # 1. 상품 조회
    product_ids = [item.product_id for item in dto.items]
    products = self.product_repository.find_by_ids(product_ids)

    # 2. (상품, 수량) 튜플 생성
    products_and_quantities = [
        (product_map[item.product_id], Quantity(item.quantity))
        for item in dto.items
    ]

    # 3. 도메인 서비스로 주문 생성
    order = OrderDomainService.create_order_with_items(
        user_id=dto.user_id,
        products_and_quantities=products_and_quantities
    )

    # 4. 재고 예약
    OrderDomainService.reserve_inventory_for_order(order, products)

    # 5. 저장
    for product in products:
        self.product_repository.save(product)
    saved_order = self.order_repository.save(order)

    # 6. DTO 변환 후 반환
    return self._to_dto(saved_order)
```

#### 4. Domain Layer (Domain Service)
```python
# domain/services.py
@staticmethod
def create_order_with_items(
    user_id: int,
    products_and_quantities: List[Tuple[Product, Quantity]]
) -> Order:
    # 1. 재고 검증
    for product, quantity in products_and_quantities:
        if not product.has_sufficient_stock(quantity):
            raise InsufficientStockError(...)

    # 2. 주문 아이템 생성
    order_items = [
        OrderItem.create_from_product(product, quantity)
        for product, quantity in products_and_quantities
    ]

    # 3. 주문 생성
    return Order.create(user_id=user_id, items=order_items)
```

#### 5. Infrastructure Layer (Repository)
```python
# infrastructure/repositories.py
def save(self, order: Order) -> Order:
    # 1. 도메인 → ORM 변환
    order_orm = OrderMapper.to_orm(order)
    order_orm.save()

    # 2. 주문 아이템 저장
    for item in order.items:
        product_orm = ProductORM.objects.get(id=item.product_id)
        item_orm = OrderItemMapper.to_orm(item, order_orm, product_orm)
        item_orm.save()

    # 3. ORM → 도메인 변환 후 반환
    order_orm.refresh_from_db()
    return OrderMapper.to_domain(order_orm)
```

### 주문 취소 플로우

```python
# API 요청
POST /api/shop/orders/1/cancel/

# Use Case
class CancelOrderUseCase:
    @transaction.atomic
    def execute(self, order_id: int) -> OrderDTO:
        # 1. 주문 조회
        order = self.order_repository.find_by_id(order_id)

        # 2. 취소 가능 여부 확인 (도메인 로직)
        if not order.can_be_cancelled():
            raise ValueError("Order cannot be cancelled")

        # 3. 상품 조회
        products = self.product_repository.find_by_ids(product_ids)

        # 4. 재고 복원 (도메인 서비스)
        OrderDomainService.restore_inventory_for_order(order, products)

        # 5. 재고 저장
        for product in products:
            self.product_repository.save(product)

        # 6. 주문 취소 (도메인 로직)
        order.cancel()

        # 7. 주문 저장
        saved_order = self.order_repository.save(order)

        return self._to_dto(saved_order)
```

## 마이그레이션 가이드

### 1. 기존 코드베이스에서 마이그레이션

#### 단계 1: 도메인 레이어 작성
1. Value Objects 정의
2. Entities 정의
3. Domain Services 정의
4. Repository Interfaces 정의

#### 단계 2: 인프라 레이어 작성
1. ORM Models 작성 (기존 models.py 이동)
2. Mappers 작성
3. Repository Implementations 작성

#### 단계 3: 애플리케이션 레이어 작성
1. DTOs 정의
2. Use Cases 작성

#### 단계 4: 프레젠테이션 레이어 리팩토링
1. Serializers에서 비즈니스 로직 제거
2. Views를 Use Cases 사용하도록 변경

#### 단계 5: 기존 파일 업데이트
1. models.py → ORM Models import
2. serializers.py → Presentation Serializers import
3. views.py → Presentation Views import

### 2. 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
python manage.py makemigrations shop

# 마이그레이션 적용
python manage.py migrate shop
```

### 3. 테스트 작성

```python
# tests/domain/test_entities.py
def test_product_reserve_stock():
    product = Product(
        id=1,
        name="Test Product",
        price=Money.from_decimal(Decimal("10000")),
        stock=Quantity(10)
    )

    product.reserve_stock(Quantity(3))

    assert product.stock == Quantity(7)

# tests/application/test_use_cases.py
def test_create_order_use_case():
    # Given
    product_repository = Mock(spec=ProductRepository)
    order_repository = Mock(spec=OrderRepository)
    use_case = CreateOrderUseCase(order_repository, product_repository)

    # When
    order_dto = use_case.execute(create_order_dto)

    # Then
    assert order_dto.status == "pending"
    assert len(order_dto.items) == 2
```

## 추가 개선 사항

### 추후 적용 가능한 패턴

1. **Event Sourcing**: 주문 상태 변경 이벤트 저장
2. **CQRS**: Command와 Query 분리
3. **Domain Events**: 주문 생성 시 이벤트 발행
4. **Specification Pattern**: 복잡한 조회 조건 캡슐화
5. **Factory Pattern**: 복잡한 객체 생성 로직 분리

### 성능 최적화

1. **N+1 Query 해결**: Repository에서 prefetch_related 사용
2. **캐싱**: Redis를 통한 상품 정보 캐싱
3. **비동기 처리**: Celery를 통한 주문 처리

## 참고 자료

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) by Robert C. Martin
- [Domain-Driven Design](https://www.domainlanguage.com/ddd/) by Eric Evans
- [Clean Code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/) by Robert C. Martin
