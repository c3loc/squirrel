from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from squirrel.orders.models import (
    Event,
    Order,
    Pillage,
    Product,
    Purchase,
    Stockpile,
    Team,
    Vendor,
)


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
        """ test that a product needs to have a name """
        product = Product()
        self.assertRaises(IntegrityError, product.save)

    def test_rename_possible(self):
        """ [regression] check that a product can be renamed. This broke when stockpiles referenced products by name, not by id """
        product = Product.objects.create(name="Rename me!")
        Stockpile.objects.create(product=product, amount=1, unit_price=499)

        product.name = "I was renamed."

        # If products can’t be renamed, this will raise an IntegrityError
        product.save()


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


class StockpilePillageModelTests(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(name="Procurement")
        self.product = Product.objects.create(name="Dr. Cave Johnson")
        self.event = Event.objects.create(name="No Conference")
        self.stockpile = Stockpile.objects.create(
            amount=10, product=self.product, unit_price=13370
        )

    def test_stockpile_stock_calculation(self):
        self.assertEqual(self.stockpile.stock, 10)

        order = Order.objects.create(
            amount=7, product=self.product, event=self.event, team=self.team
        )
        Pillage.objects.create(amount=3, order=order, stockpile=self.stockpile)
        self.assertEqual(self.stockpile.stock, 7)

    def test_pillage_order_fulfilled(self):
        order = Order.objects.create(
            amount=7, product=self.product, event=self.event, team=self.team
        )
        pillage = Pillage(amount=8, order=order, stockpile=self.stockpile)
        self.assertRaisesRegex(
            ValidationError,
            "The order only is for 7. With this pillage of 8, it would go to 8.",
            pillage.save,
        )

    def test_pillage_stockpile_too_small(self):
        order = Order.objects.create(
            amount=15, product=self.product, event=self.event, team=self.team
        )
        pillage = Pillage(amount=12, order=order, stockpile=self.stockpile)

        self.assertRaisesRegex(
            ValidationError,
            "The stockpile has 10 available, you requested 12.",
            pillage.save,
        )

    def test_pillage_order_exact_amount(self):
        order = Order.objects.create(
            amount=8, product=self.product, event=self.event, team=self.team
        )
        self.failUnless(
            Pillage.objects.create(amount=8, order=order, stockpile=self.stockpile)
        )

    def test_pillage_order_two_pillages_exact_amount(self):
        order = Order.objects.create(
            amount=8, product=self.product, event=self.event, team=self.team
        )

        self.failUnless(
            Pillage.objects.create(amount=3, order=order, stockpile=self.stockpile)
        )
        self.failUnless(
            Pillage.objects.create(amount=5, order=order, stockpile=self.stockpile)
        )
