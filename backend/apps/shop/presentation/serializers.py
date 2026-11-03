"""
API Serializers for Shop domain.

Serializers handle request/response data serialization and validation.
They should NOT contain business logic.
"""
from decimal import Decimal
from rest_framework import serializers

from ..application.dto import (
    CreateOrderDTO,
    CreateProductDTO,
    OrderDTO,
    OrderItemDTO,
    OrderItemRequestDTO,
    ProductDTO,
    UpdateOrderStatusDTO,
    UpdateProductDTO,
)


class ProductSerializer(serializers.Serializer):
    """상품 Serializer"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=200)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField(min_value=0)
    description = serializers.CharField(allow_blank=True, default="")
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_dto(self) -> CreateProductDTO:
        """Serializer 데이터를 CreateProductDTO로 변환"""
        return CreateProductDTO(
            name=self.validated_data["name"],
            price=self.validated_data["price"],
            stock=self.validated_data["stock"],
            description=self.validated_data.get("description", "")
        )

    def to_update_dto(self) -> UpdateProductDTO:
        """Serializer 데이터를 UpdateProductDTO로 변환"""
        return UpdateProductDTO(
            name=self.validated_data.get("name"),
            price=self.validated_data.get("price"),
            stock=self.validated_data.get("stock"),
            description=self.validated_data.get("description")
        )

    @staticmethod
    def from_dto(dto: ProductDTO) -> dict:
        """ProductDTO를 딕셔너리로 변환"""
        return {
            "id": dto.id,
            "name": dto.name,
            "price": dto.price,
            "stock": dto.stock,
            "description": dto.description,
            "created_at": dto.created_at,
            "updated_at": dto.updated_at
        }


class OrderItemRequestSerializer(serializers.Serializer):
    """주문 아이템 요청 Serializer"""
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

    def to_dto(self) -> OrderItemRequestDTO:
        """Serializer 데이터를 OrderItemRequestDTO로 변환"""
        return OrderItemRequestDTO(
            product_id=self.validated_data["product_id"],
            quantity=self.validated_data["quantity"]
        )


class OrderItemSerializer(serializers.Serializer):
    """주문 아이템 응답 Serializer"""
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    @staticmethod
    def from_dto(dto: OrderItemDTO) -> dict:
        """OrderItemDTO를 딕셔너리로 변환"""
        return {
            "id": dto.id,
            "product_id": dto.product_id,
            "product_name": dto.product_name,
            "quantity": dto.quantity,
            "unit_price": dto.unit_price,
            "line_total": dto.line_total
        }


class CreateOrderSerializer(serializers.Serializer):
    """주문 생성 요청 Serializer"""
    items = OrderItemRequestSerializer(many=True)

    def validate_items(self, value):
        """주문 아이템 검증"""
        if not value:
            raise serializers.ValidationError("Order must have at least one item")
        return value

    def to_dto(self, user_id: int) -> CreateOrderDTO:
        """Serializer 데이터를 CreateOrderDTO로 변환"""
        items_dto = [
            OrderItemRequestDTO(
                product_id=item["product_id"],
                quantity=item["quantity"]
            )
            for item in self.validated_data["items"]
        ]

        return CreateOrderDTO(
            user_id=user_id,
            items=items_dto
        )


class OrderSerializer(serializers.Serializer):
    """주문 응답 Serializer"""
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    @staticmethod
    def from_dto(dto: OrderDTO) -> dict:
        """OrderDTO를 딕셔너리로 변환"""
        return {
            "id": dto.id,
            "user_id": dto.user_id,
            "status": dto.status,
            "total_amount": dto.total_amount,
            "items": [OrderItemSerializer.from_dto(item) for item in dto.items],
            "created_at": dto.created_at
        }


class UpdateOrderStatusSerializer(serializers.Serializer):
    """주문 상태 업데이트 Serializer"""
    status = serializers.ChoiceField(choices=[
        "pending",
        "confirmed",
        "paid",
        "shipped",
        "delivered",
        "cancelled",
        "refunded"
    ])

    def to_dto(self) -> UpdateOrderStatusDTO:
        """Serializer 데이터를 UpdateOrderStatusDTO로 변환"""
        return UpdateOrderStatusDTO(
            status=self.validated_data["status"]
        )
