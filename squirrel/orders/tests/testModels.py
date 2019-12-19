from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from orders.models import Event, Order, Product, Team, Vendor


class EventModelTests(TestCase):
    def test_require_name(self):
        event = Event()
        self.assertRaises(IntegrityError, event.save)


class TeamModelTests(TestCase):
    def test_require_name(self):
        team = Team()
        self.assertRaises(IntegrityError, team.save)


class VendorModelTests(TestCase):
    def test_require_name(self):
        vendor = Vendor()
        self.assertRaises(IntegrityError, vendor.save)


class ProductModelTests(TestCase):
    def test_inherit_product_price(self):
        product = Product.objects.create(name="Tardis", unit_price=17.00)
        team = Team.objects.create(name="Aperture Science Laboratories")
        order = Order.objects.create(product=product, team=team)
        completed_order = Order.objects.create(product=product, team=team, state="COM")

        product.unit_price = 23.03
        product.save()

        self.assertEqual(Order.objects.get(id=order.id).unit_price, Decimal("23.03"))
        self.assertEqual(
            Order.objects.get(id=completed_order.id).unit_price, Decimal("17.00")
        )

    def test_require_name(self):
        product = Product()
        self.assertRaises(IntegrityError, product.save)


class OrderModelTests(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(name="Aperture Science Laboratories")
        self.product = Product.objects.create(name="Dr. Cave Johnson", unit_price=23.42)

    def test_amount_must_be_positive(self):
        order = Order.objects.create(product=self.product, team=self.team)
        order.amount = -1
        self.assertRaises(IntegrityError, order.save)

    def test_product_or_suggestion_must_be_given(self):
        order = Order(team=self.team)
        self.assertRaises(ValidationError, order.full_clean)

    def test_product_and_suggestion_not_allowed(self):
        order = Order(
            product=self.product, product_suggestion="Antonov An-225 ", team=self.team
        )
        self.assertRaises(ValidationError, order.full_clean)

    def test_inherit_product_price_on_create(self):
        order = Order.objects.create(product=self.product, team=self.team)
        self.assertEqual(order.unit_price, 23.42)

    def test_forbid_completed_order_deletion(self):
        order = Order.objects.create(product=self.product, team=self.team, state="COM")
        self.assertRaises(PermissionDenied, order.delete)
