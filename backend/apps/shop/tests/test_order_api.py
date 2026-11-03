"""주문 API 통합 테스트: 재고 차감/복원과 권한 검사."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.shop.models import Product

User = get_user_model()


class OrderAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw")
        self.other = User.objects.create_user(username="other", password="pw")
        self.admin = User.objects.create_user(username="admin", password="pw", is_staff=True)
        self.product = Product.objects.create(name="Keyboard", price=Decimal("50000"), stock=10)

    def _create_order(self, quantity=2):
        self.client.force_authenticate(self.owner)
        res = self.client.post(
            "/api/shop/orders/",
            {"items": [{"product_id": self.product.id, "quantity": quantity}]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        return res.data

    def _stock(self):
        self.product.refresh_from_db()
        return self.product.stock

    def test_create_order_reserves_stock_and_totals(self):
        order = self._create_order(quantity=3)
        self.assertEqual(Decimal(order["total_amount"]), Decimal("150000"))
        self.assertEqual(order["items"][0]["product_name"], "Keyboard")
        self.assertEqual(self._stock(), 7)

    def test_create_order_rejects_insufficient_stock(self):
        self.client.force_authenticate(self.owner)
        res = self.client.post(
            "/api/shop/orders/",
            {"items": [{"product_id": self.product.id, "quantity": 11}]},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self._stock(), 10)

    def test_owner_cancel_restores_stock(self):
        order = self._create_order(quantity=2)
        res = self.client.post(f"/api/shop/orders/{order['id']}/cancel/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "cancelled")
        self.assertEqual(self._stock(), 10)

    def test_other_user_cannot_cancel(self):
        order = self._create_order(quantity=2)
        self.client.force_authenticate(self.other)
        res = self.client.post(f"/api/shop/orders/{order['id']}/cancel/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        # 거부된 요청은 주문/재고를 바꾸지 않아야 한다
        self.assertEqual(self._stock(), 8)
        self.client.force_authenticate(self.owner)
        res = self.client.get(f"/api/shop/orders/{order['id']}/")
        self.assertEqual(res.data["status"], "pending")

    def test_other_user_cannot_view_order(self):
        order = self._create_order()
        self.client.force_authenticate(self.other)
        res = self.client.get(f"/api/shop/orders/{order['id']}/")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_staff_cannot_update_status(self):
        order = self._create_order()
        res = self.client.post(
            f"/api/shop/orders/{order['id']}/update_status/", {"status": "confirmed"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_update_status_with_valid_transition(self):
        order = self._create_order()
        self.client.force_authenticate(self.admin)
        url = f"/api/shop/orders/{order['id']}/update_status/"
        res = self.client.post(url, {"status": "confirmed"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "confirmed")
        # pending 으로 되돌리는 전환은 허용되지 않음
        res = self.client.post(url, {"status": "pending"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
