from django.test import TestCase
from orders.models import Team, Vendor


class ProductRegressionTests(TestCase):
    """Regression tests for products"""

    def setUp(self) -> None:
        self.vendor = Vendor.objects.create(name="Insert Company here")
        self.team = Team.objects.create(name="Cave Johnson")
