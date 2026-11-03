"""
Domain Exceptions for Shop domain.

Custom exceptions that represent domain-specific error conditions.
"""


class ShopDomainError(Exception):
    """Shop 도메인 기본 예외"""
    pass


class InsufficientStockError(ShopDomainError):
    """재고 부족 예외"""
    pass


class InvalidOrderStateError(ShopDomainError):
    """잘못된 주문 상태 예외"""
    pass


class InvalidPriceError(ShopDomainError):
    """잘못된 가격 예외"""
    pass


class InvalidQuantityError(ShopDomainError):
    """잘못된 수량 예외"""
    pass


class ProductNotFoundError(ShopDomainError):
    """상품을 찾을 수 없음 예외"""
    pass


class OrderNotFoundError(ShopDomainError):
    """주문을 찾을 수 없음 예외"""
    pass
