"""
API Views for Shop app.

This file imports views from presentation layer to maintain
Django's convention while following Clean Architecture.
"""
from .presentation.views import OrderViewSet, ProductViewSet

__all__ = ["ProductViewSet", "OrderViewSet"]
