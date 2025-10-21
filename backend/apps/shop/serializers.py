"""
API Serializers for Shop app.

This file imports serializers from presentation layer to maintain
Django's convention while following Clean Architecture.
"""
from .presentation.serializers import (
    CreateOrderSerializer,
    OrderItemRequestSerializer,
    OrderItemSerializer,
    OrderSerializer,
    ProductSerializer,
    UpdateOrderStatusSerializer,
)

__all__ = [
    "ProductSerializer",
    "OrderItemRequestSerializer",
    "OrderItemSerializer",
    "CreateOrderSerializer",
    "OrderSerializer",
    "UpdateOrderStatusSerializer",
]
