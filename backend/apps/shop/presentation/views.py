"""
API Views for Shop domain.

Views handle HTTP requests/responses and delegate business logic to use cases.
They should be thin and focus on HTTP concerns.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..application.use_cases import (
    CancelOrderUseCase,
    CreateOrderUseCase,
    CreateProductUseCase,
    GetOrderUseCase,
    GetProductUseCase,
    ListProductsUseCase,
    ListUserOrdersUseCase,
    UpdateOrderStatusUseCase,
    UpdateProductUseCase,
)
from ..domain.exceptions import (
    InsufficientStockError,
    InvalidOrderStateError,
    OrderNotFoundError,
    ProductNotFoundError,
    ShopDomainError,
)
from ..infrastructure.repositories import DjangoOrderRepository, DjangoProductRepository
from .serializers import (
    CreateOrderSerializer,
    OrderSerializer,
    ProductSerializer,
    UpdateOrderStatusSerializer,
)


class ProductViewSet(viewsets.ViewSet):
    """상품 API ViewSet"""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_repository = DjangoProductRepository()

    def list(self, request):
        """상품 목록 조회"""
        try:
            use_case = ListProductsUseCase(self.product_repository)
            products_dto = use_case.execute()

            data = [ProductSerializer.from_dto(dto) for dto in products_dto]
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """상품 상세 조회"""
        try:
            use_case = GetProductUseCase(self.product_repository)
            product_dto = use_case.execute(int(pk))

            data = ProductSerializer.from_dto(product_dto)
            return Response(data, status=status.HTTP_200_OK)

        except ProductNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """상품 생성"""
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = CreateProductUseCase(self.product_repository)
            product_dto = use_case.execute(serializer.to_dto())

            data = ProductSerializer.from_dto(product_dto)
            return Response(data, status=status.HTTP_201_CREATED)

        except ShopDomainError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, pk=None):
        """상품 전체 업데이트"""
        serializer = ProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = UpdateProductUseCase(self.product_repository)
            product_dto = use_case.execute(int(pk), serializer.to_update_dto())

            data = ProductSerializer.from_dto(product_dto)
            return Response(data, status=status.HTTP_200_OK)

        except ProductNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ShopDomainError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def partial_update(self, request, pk=None):
        """상품 부분 업데이트"""
        serializer = ProductSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = UpdateProductUseCase(self.product_repository)
            product_dto = use_case.execute(int(pk), serializer.to_update_dto())

            data = ProductSerializer.from_dto(product_dto)
            return Response(data, status=status.HTTP_200_OK)

        except ProductNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except ShopDomainError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrderViewSet(viewsets.ViewSet):
    """주문 API ViewSet"""
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.order_repository = DjangoOrderRepository()
        self.product_repository = DjangoProductRepository()

    def list(self, request):
        """주문 목록 조회 (현재 사용자)"""
        try:
            use_case = ListUserOrdersUseCase(self.order_repository)
            orders_dto = use_case.execute(request.user.id)

            data = [OrderSerializer.from_dto(dto) for dto in orders_dto]
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, pk=None):
        """주문 상세 조회"""
        try:
            use_case = GetOrderUseCase(self.order_repository)
            order_dto = use_case.execute(int(pk))

            # 권한 확인: 자신의 주문만 조회 가능
            if order_dto.user_id != request.user.id and not request.user.is_superuser:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )

            data = OrderSerializer.from_dto(order_dto)
            return Response(data, status=status.HTTP_200_OK)

        except OrderNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """주문 생성"""
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = CreateOrderUseCase(
                self.order_repository,
                self.product_repository
            )
            order_dto = use_case.execute(serializer.to_dto(request.user.id))

            data = OrderSerializer.from_dto(order_dto)
            return Response(data, status=status.HTTP_201_CREATED)

        except ProductNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except InsufficientStockError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ShopDomainError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """주문 상태 업데이트"""
        # 권한 확인: 주문 상태 변경(결제/배송 등)은 관리자만 가능
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UpdateOrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            use_case = UpdateOrderStatusUseCase(self.order_repository)
            order_dto = use_case.execute(int(pk), serializer.to_dto())

            data = OrderSerializer.from_dto(order_dto)
            return Response(data, status=status.HTTP_200_OK)

        except OrderNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except InvalidOrderStateError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ShopDomainError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """주문 취소"""
        try:
            # 권한 확인: 취소(재고 복원)를 실행하기 전에 소유자인지 먼저 확인
            order = GetOrderUseCase(self.order_repository).execute(int(pk))
            if order.user_id != request.user.id and not request.user.is_superuser:
                return Response(
                    {"error": "Permission denied"},
                    status=status.HTTP_403_FORBIDDEN
                )

            use_case = CancelOrderUseCase(
                self.order_repository,
                self.product_repository
            )
            order_dto = use_case.execute(int(pk))

            data = OrderSerializer.from_dto(order_dto)
            return Response(data, status=status.HTTP_200_OK)

        except OrderNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except (InvalidOrderStateError, ValueError) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ShopDomainError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
