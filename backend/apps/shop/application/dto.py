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
    """상품 생성 요청 DTO"""
    name: str
    price: Decimal
    stock: int
    description: str = ""


@dataclass
class UpdateProductDTO:
    """상품 업데이트 요청 DTO"""
    name: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    description: Optional[str] = None


@dataclass
class ProductDTO:
    """상품 응답 DTO"""
    id: int
    name: str
    price: Decimal
    stock: int
    description: str
    created_at: datetime
    updated_at: datetime


@dataclass
class OrderItemRequestDTO:
    """주문 아이템 요청 DTO"""
    product_id: int
    quantity: int


@dataclass
class OrderItemDTO:
    """주문 아이템 응답 DTO"""
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


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


@dataclass
class UpdateOrderStatusDTO:
    """주문 상태 업데이트 요청 DTO"""
    status: str
