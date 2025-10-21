"""Domain layer for Shop application."""
from .entities import Order, OrderItem, Product
from .exceptions import (
    InsufficientStockError,
    InvalidOrderStateError,
    InvalidPriceError,
    InvalidQuantityError,
    OrderNotFoundError,
    ProductNotFoundError,
    ShopDomainError,
)
from .repositories import OrderRepository, ProductRepository
from .services import InventoryDomainService, OrderDomainService
from .value_objects import Money, OrderStatus, Quantity

__all__ = [
    # Entities
    "Product",
    "OrderItem",
    "Order",
    # Value Objects
    "Money",
    "OrderStatus",
    "Quantity",
    # Services
    "OrderDomainService",
    "InventoryDomainService",
    # Repositories
    "ProductRepository",
    "OrderRepository",
    # Exceptions
    "ShopDomainError",
    "InsufficientStockError",
    "InvalidOrderStateError",
    "InvalidPriceError",
    "InvalidQuantityError",
    "ProductNotFoundError",
    "OrderNotFoundError",
]
