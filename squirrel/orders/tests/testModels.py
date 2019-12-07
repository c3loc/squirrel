from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.utils import IntegrityError
from django.test import TestCase
from orders.models import Order, Product, Team


class ProductModelTests(TestCase):
    def setUp(self) -> None:
        # https://github.com/moby/moby/blob/3152f9436292115c97b4d8bb18c66cf97876ee75/pkg/namesgenerator/names-generator.go#L838-L840
        User.objects.create_user("Boring Wozniak")
        Team.objects.create(name="Aperture Science Laboratories")

        Product.objects.create(name="Tardis", unit_price=17.00)

        Order.objects.create(
            amount=23,
            product=Product.objects.first(),
            team=Team.objects.first(),
            unit_price=13.57,
        )

    def test_inherit_product_price(self):
        product = Product.objects.first()

        product.unit_price = 23.03
        product.save()

        # This order has to change its unit_price as it’s not completed yet
        order_price_change = Order.objects.first()
        self.assertEqual(order_price_change.unit_price, Decimal("23.03"))

    def test_require_name(self):
        product = Product()
        self.assertRaises(IntegrityError, product.save)


class OrderModelTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user("Wheatly")
        Team.objects.create(name="Aperture Science Laboratories")

        Product.objects.create(name="Dr. Cave Johnson", unit_price=23.42)
        Order.objects.create(
            product=Product.objects.first(), team=Team.objects.first(),
        )

    def test_inherit_product_price_on_create(self):
        order = Order.objects.first()

        # The order has to have the products unit_price as it was not specified on creation
        self.assertEqual(order.unit_price, Decimal("23.42"))

    def test_forbid_completed_order_deletion_or_update(self):
        order = Order.objects.first()

        order.state = "COM"
        order.save()

        # The order is now completed and must not be deleted
        self.assertRaises(PermissionDenied, order.delete())

        # The order must also not be changed once it’s completed
        order.amount = 1337
        self.assertRaises(PermissionDenied, order.save())
