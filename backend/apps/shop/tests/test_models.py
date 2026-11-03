from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.shop.models import Order, OrderItem, Product

User = get_user_model()


class EcommerceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="1234")
        self.product = Product.objects.create(name="Test Product", price=1000, stock=10)

    def test_order_create(self):
        order = Order.objects.create(user=self.user)
        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            product_name=self.product.name,
            quantity=2,
            unit_price=self.product.price,
        )
        order.total_amount = item.unit_price * item.quantity
        order.save()
        self.assertEqual(order.total_amount, 2000)
