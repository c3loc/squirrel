from django.test import TestCase
from orders.models import Order, Product, Team, Vendor


class ProductRegressionTests(TestCase):
    """Regression tests for products"""

    def setUp(self) -> None:
        self.vendor = Vendor.objects.create(name="Insert Company here")
        self.team = Team.objects.create(name="Cave Johnson")

    def test_dont_update_orders_without_product(self):
        """Creation of products does not update prices of orders without product"""

        """ This tests against a bug where on creating a product, unit_prices of orders without a product were updated
            The case of the bug was that the order prices were first updated and the product saved afterwards.
            On creation of a new product, that meant that the query
                orders = Order.objects.filter(product=self)
            matched only orders where the product was None as the product is not yet saved.
        """
        Order.objects.create(
            team=self.team,
            product_suggestion="The same price. Always.",
            unit_price=10.00,
        )
        Product.objects.create(
            name="Change the order price", vendor=self.vendor, unit_price=17.43
        )

        # Get the order from the database
        order = Order.objects.get(product_suggestion="The same price. Always.")

        self.assertEqual(order.unit_price, 10.00)
