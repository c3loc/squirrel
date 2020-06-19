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

    def test_automatic_pillaging(self):
        stockpile = Stockpile.objects.create(
            product=self.product, amount=17, unit_price=990
        )
        Order.objects.create(product=self.product, amount=13, team=self.team)
        pillages = Pillage.objects.all()

        # Check that exactly one pillage is created
        self.assertEqual(len(pillages), 1)

        # Check that this pillage takes 13 of the product
        self.assertEqual(pillages[0].amount, 13)

        # Check that the stockpile has 4 remaining
        self.assertEqual(stockpile.stock, 4)

        # Create a second order to test that pillages are emtied correctly
        Order.objects.create(product=self.product, amount=10, team=self.team)
        pillages = Pillage.objects.all()

        self.assertEqual(len(pillages), 2)

        # The pillage for the second order can only have four as the stockpile has 17
        self.assertEqual(pillages[1].amount, 4)

        self.assertEqual(stockpile.stock, 0)


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
        self.wrong_product = Product.objects.create(name="Wrong product.")
        self.event = Event.objects.create(name="No Conference")
        self.stockpile = Stockpile.objects.create(
            amount=10, product=self.product, unit_price=13370
        )
        self.wrong_stockpile = Stockpile.objects.create(
            amount=10, product=self.wrong_product, unit_price=23420
        )

    def test_product_is_checked(self):
        order = Order.objects.create(
            amount=7, product=self.product, event=self.event, team=self.team
        )

        pillage = Pillage(amount=5, order=order, stockpile=self.wrong_stockpile)
        self.assertRaisesRegex(
            ValidationError,
            "The product of the order and the stockpile it is taken from have to match!",
            pillage.save,
        )

    def test_stockpile_stock_calculation(self):
        self.assertEqual(self.stockpile.stock, 10)

        Order.objects.create(
            amount=7, product=self.product, event=self.event, team=self.team
        )
        self.assertEqual(self.stockpile.stock, 3)

    def test_pillage_order_fulfilled(self):
        order = Order.objects.create(
            amount=7, product=self.product, event=self.event, team=self.team
        )
        pillage = Pillage(amount=8, order=order, stockpile=self.stockpile)
        self.assertRaisesRegex(
            ValidationError,
            "The order only is for 7. With this pillage of 8, it would go to 15.",
            pillage.save,
        )

    def test_pillage_stockpile_too_small(self):
        order = Order.objects.create(
            amount=15, product=self.product, event=self.event, team=self.team
        )
        pillage = Pillage(amount=4, order=order, stockpile=self.stockpile)

        self.assertRaisesRegex(
            ValidationError,
            "The stockpile has 0 available, you requested 4.",
            pillage.save,
        )

    def test_stockpile_save_fills_orders(self):
        # This order will be filled with the existing stockpile of 10, so there are 110 to be pillaged
        Order.objects.create(product=self.product, team=self.team, amount=120)

        # This must create a second pillage with 90, so there are 20 left
        Stockpile.objects.create(product=self.product, amount=90, unit_price=42000)

        # Check that two pillages exist and their amounts
        pillages = Pillage.objects.all()

        self.assertEqual(len(pillages), 2)
        self.assertEqual(pillages[0].amount, 10)
        self.assertEqual(pillages[1].amount, 90)

        # Create a third stockpile that has more than enough to fill the order
        # With this we test that not more than necessary is taken
        Stockpile.objects.create(product=self.product, amount=100, unit_price=42000)

        # Check the pillages again
        pillages = Pillage.objects.all()

        self.assertEqual(len(pillages), 3)
        self.assertEqual(pillages[0].amount, 10)
        self.assertEqual(pillages[1].amount, 90)
        self.assertEqual(pillages[2].amount, 20)

        # Check that the last stockpile has 80 left
        self.assertEqual(Stockpile.objects.get(amount=100).stock, 80)
