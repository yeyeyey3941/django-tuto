"""
Django ORM Models for Shop app.

This file imports ORM models from infrastructure layer to maintain
Django's convention while following Clean Architecture.
"""
from .infrastructure.orm_models import OrderItemORM as OrderItem
from .infrastructure.orm_models import OrderORM as Order
from .infrastructure.orm_models import ProductORM as Product

# Export models for Django admin and migrations
__all__ = ["Product", "Order", "OrderItem"]
