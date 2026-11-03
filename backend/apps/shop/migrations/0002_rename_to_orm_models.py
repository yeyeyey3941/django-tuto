"""
Shop 모델을 infrastructure/orm_models.py 의 *ORM 클래스로 옮긴 변경을 반영한다.

자동 생성(makemigrations)은 테이블을 삭제 후 재생성하므로 기존 데이터가 사라진다.
이 마이그레이션은 이름 변경만 수행해 기존 상품/주문 데이터를 보존한다.
"""
from django.conf import settings
from django.db import migrations, models


def fill_product_name(apps, schema_editor):
    """기존 주문 아이템의 product_name 을 현재 상품명으로 채운다."""
    OrderItemORM = apps.get_model("shop", "OrderItemORM")
    for item in OrderItemORM.objects.select_related("product").all():
        item.product_name = item.product.name
        item.save(update_fields=["product_name"])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("shop", "0001_initial"),
    ]

    operations = [
        # 1) 테이블 이름 고정 (product/order 는 기존 이름 그대로, orderitem 만 변경)
        migrations.AlterModelTable(name="product", table="shop_product"),
        migrations.AlterModelTable(name="order", table="shop_order"),
        migrations.AlterModelTable(name="orderitem", table="shop_order_item"),
        # 2) 모델 클래스 이름 변경 (db_table 이 고정돼 있어 실제 테이블은 그대로)
        migrations.RenameModel(old_name="Product", new_name="ProductORM"),
        migrations.RenameModel(old_name="Order", new_name="OrderORM"),
        migrations.RenameModel(old_name="OrderItem", new_name="OrderItemORM"),
        # 3) 주문 아이템 필드 변경: price -> unit_price, product_name 추가
        migrations.RenameField(
            model_name="orderitemorm", old_name="price", new_name="unit_price"
        ),
        migrations.AddField(
            model_name="orderitemorm",
            name="product_name",
            field=models.CharField(default="", max_length=200),
            preserve_default=False,
        ),
        migrations.RunPython(fill_product_name, migrations.RunPython.noop),
        # 4) Meta 옵션 및 인덱스
        migrations.AlterModelOptions(
            name="productorm",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Product",
                "verbose_name_plural": "Products",
            },
        ),
        migrations.AlterModelOptions(
            name="orderorm",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Order",
                "verbose_name_plural": "Orders",
            },
        ),
        migrations.AlterModelOptions(
            name="orderitemorm",
            options={"verbose_name": "Order Item", "verbose_name_plural": "Order Items"},
        ),
        migrations.AddIndex(
            model_name="orderorm",
            index=models.Index(
                fields=["user", "-created_at"], name="shop_order_user_id_f8b1c9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="orderorm",
            index=models.Index(fields=["status"], name="shop_order_status_63c2c0_idx"),
        ),
    ]
