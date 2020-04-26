from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from squirrel.orders.models import Event, Order, Product, Purchase, Team, Vendor


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
    def test_require_name(self):
        product = Product()
        self.assertRaises(IntegrityError, product.save)


class OrderModelTests(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(name="Aperture Science Laboratories")
        self.product = Product.objects.create(name="Dr. Cave Johnson")

    def test_amount_must_be_positive(self):
        order = Order.objects.create(product=self.product, team=self.team)
        order.amount = -1
        self.assertRaises(IntegrityError, order.save)

    def test_product_must_be_given(self):
        order = Order(team=self.team)
        self.assertRaises(ValidationError, order.full_clean)


class PurchaseModelTests(TestCase):
    def setUp(self) -> None:
        self.vendor = Vendor.objects.create(name="Aperture Science Laboratories")
        self.team = Team.objects.create(name="Procurement")
        self.product = Product.objects.create(name="Dr. Cave Johnson")
        self.purchase = Purchase.objects.create(vendor=self.vendor)
        self.order_req = Order.objects.create(
            product=self.product, team=self.team, amount=27, state="REQ"
        )
        self.order_app = Order.objects.create(
            product=self.product, team=self.team, amount=23, state="APP"
        )
