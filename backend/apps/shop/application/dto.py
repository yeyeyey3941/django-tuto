"""
Data Transfer Objects (DTOs) for Shop application.

DTOs define the structure of data passed between layers.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass
class CreateProductDTO:
    """Áˆ Ý1 ”­ DTO"""
    name: str
    price: Decimal
    stock: int
    description: str = ""


@dataclass
class UpdateProductDTO:
    """Áˆ Åpt¸ ”­ DTO"""
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    description: Optional[str] = None


@dataclass
class ProductDTO:
    """Áˆ Qõ DTO"""
    id: int
    name: str
    price: Decimal
    stock: int
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass
class OrderItemRequestDTO:
    """ü8 Dt\ ”­ DTO"""
    product_id: int
    quantity: int


@dataclass
class OrderItemDTO:
    """ü8 Dt\ Qõ DTO"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


@dataclass
class CreateOrderDTO:
    """ü8 Ý1 ”­ DTO"""
    user_id: int
    items: List[OrderItemRequestDTO]


@dataclass
class OrderDTO:
    """ü8 Qõ DTO"""
    id: int
    user_id: int
    status: str
    total_amount: Decimal
    items: List[OrderItemDTO]
    created_at: datetime


@dataclass
class UpdateOrderStatusDTO:
    """ü8 ÁÜ Åpt¸ ”­ DTO"""
    status: str
