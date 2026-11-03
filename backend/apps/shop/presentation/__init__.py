"""Presentation layer for Shop application."""
from .serializers import (
    CreateOrderSerializer,
    OrderItemRequestSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductSerializer,
    UpdateOrderStatusSerializer,
)
from .views import OrderViewSet, ProductViewSet

__all__ = [
    # Serializers
    "ProductSerializer",
    "OrderItemRequestSerializer",
    "OrderItemSerializer",
    "CreateOrderSerializer",
    "OrderSerializer",
    "UpdateOrderStatusSerializer",
    # Views
    "ProductViewSet",
    "OrderViewSet",
]
