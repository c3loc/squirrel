from django.core.exceptions import PermissionDenied, ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from orders.models import Event, Good, Order, Product, Purchase, Team, Vendor


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

    def test_product_or_suggestion_must_be_given(self):
        order = Order(team=self.team)
        self.assertRaises(ValidationError, order.full_clean)

    def test_product_and_suggestion_not_allowed(self):
        order = Order(
            product=self.product, product_suggestion="Antonov An-225 ", team=self.team
        )
        self.assertRaises(ValidationError, order.full_clean)

    def test_forbid_completed_order_deletion(self):
        order = Order.objects.create(product=self.product, team=self.team, state="COM")
        self.assertRaises(PermissionDenied, order.delete)


class GoodModelTests(TestCase):
    def setUp(self) -> None:
        self.vendor = Vendor.objects.create(name="Aperture Science Laboratories")
        self.team = Team.objects.create(name="Procurement")
        self.product = Product.objects.create(name="Dr. Cave Johnson")
        self.purchase_net = Purchase.objects.create(vendor=self.vendor)
        self.purchase_gross = Purchase.objects.create(vendor=self.vendor, is_net=False)
        self.good_net = Good.objects.create(
            name="Cave", unit_price=100, amount=30, purchase=self.purchase_net
        )
        self.good_gross = Good.objects.create(
            name="Cave", unit_price=119, amount=30, purchase=self.purchase_gross
        )

        self.order = Order.objects.create(
            product=self.product, team=self.team, amount=27, good=self.good_net
        )

    def test_good_minimal_amount_is_sum_of_orders(self):
        """The minimal amount of a good_net is always the sum of its orders"""
        # This must work as it is the minimum
        self.good_net.amount = self.order.amount
        self.good_net.clean()

        # This must not work as it is below
        self.good_net.amount = self.order.amount - 1
        self.assertRaises(ValidationError, self.good_net.clean)

        # This must also not work as it would be a return
        self.good_net.amount = self.order.amount * -1
        self.assertRaises(ValidationError, self.good_net.clean)

    def test_good_gross_calculation(self):
        """Calculation of gross from net value"""
        self.assertEqual(self.good_net.gross, 3570)

    def test_good_net_calculation(self):
        """Calculation of net from gross value"""
        self.assertEqual(self.good_gross.net, 3000)


class PurchaseModelTests(TestCase):
    def setUp(self) -> None:
        self.vendor = Vendor.objects.create(name="Aperture Science Laboratories")
        self.team = Team.objects.create(name="Procurement")
        self.product = Product.objects.create(name="Dr. Cave Johnson")
        self.purchase = Purchase.objects.create(vendor=self.vendor)
        self.good = Good.objects.create(
            name="Cave", unit_price=1700, amount=50, purchase=self.purchase
        )
        self.order_req = Order.objects.create(
            product=self.product, team=self.team, amount=27, good=self.good, state="REQ"
        )
        self.order_app = Order.objects.create(
            product=self.product, team=self.team, amount=23, good=self.good, state="APP"
        )

    def test_purchase_transitive_state_setter(self):
        """Setting the state of a purchase_net sets the state of the orders"""
        self.purchase.state = "REA"

        # We need to reload the objects from the DB as the setter changes them transparently to Djangos test framework
        order_req = Order.objects.get(amount=27)
        order_app = Order.objects.get(amount=23)

        self.assertEqual(order_req.state, "REA")
        self.assertEqual(order_app.state, "REA")

    def test_purchase_sums(self):
        self.assertEqual(self.purchase.net, 85000)
        self.assertEqual(self.purchase.gross, 101150)
