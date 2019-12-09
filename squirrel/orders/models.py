"""
Models for our orders
"""
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models


class Event(models.Model):
    """An event for which orders can be made"""

    name = models.CharField(max_length=50, unique=True, default=None)

    def __str__(self):
        return self.name


class Team(models.Model):
    """A team or similar group that orders things"""

    class Meta:
        permissions = [("view_budget", "Can view budget")]

    name = models.CharField(max_length=50, unique=True, default=None)
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    """A vendor"""

    name = models.CharField(max_length=250, default=None, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product that can be ordered"""

    name = models.CharField(max_length=250, default=None)
    unit = models.CharField(max_length=20, default="pieces")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    url = models.URLField(blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Set the unit_price for all non-completed orders to the new product price"""
        orders = Order.objects.filter(product=self)

        # We exclude completed orders
        orders = orders.exclude(state="COM")

        for order in orders:
            order.unit_price = self.unit_price
            order.save()

        super().save(*args, **kwargs)


class Order(models.Model):
    """A single order. Orders are always referenced to a team"""

    class Meta:
        permissions = [
            ("request_order", "Can request a order"),
            ("approve_order", "Can approve a order"),
            ("receive_order", "Can receive order"),
            ("complete_order", "Can compelete order"),
        ]

    __old_state = None

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.__old_state = self.state

    STATE_CHOICES = [
        ("REQ", "Requested"),  # User has requested Order
        (
            "APP",
            "Approved",
        ),  # Order was approved by purchase department and will be purchased
        (
            "REA",
            "Ready for pick-up",
        ),  # Order has been delivered (and commissioned if necessary)
        ("COM", "Completed"),  # Order has been picked up by the team
    ]

    amount = models.PositiveIntegerField(default=1)

    # Either a product or a free form item have to be specified
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=True, blank=True
    )
    product_suggestion = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)

    state = models.CharField(choices=STATE_CHOICES, default="REQ", max_length=30)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="orders", blank=True, null=True
    )
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="orders")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    created_by = models.ForeignKey(
        User, null=True, related_name="orders", on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, null=True, related_name="orders_updates", on_delete=models.SET_NULL
    )

    def clean(self):
        """We need to check if either a product or a free form text are set"""
        if not self.product and not self.product_suggestion:
            raise ValidationError("An order must have either a product or an item set")
        elif self.product and self.product_suggestion:
            raise ValidationError("An order must not have a product and an item set")

    def save(self, *args, **kwargs):
        """Orders have some special behavior on saving"""

        # If no unit_price was set, set the price to the price of the product if one is set
        if not self.unit_price and self.product:
            self.unit_price = self.product.unit_price

        # If the old state was COM, the order can’t be changed anymore
        # An order can however be created in the „completed“ state, therefore the (and self.id)
        if self.__old_state == "COM" and self.id:
            raise PermissionDenied("Completed orders can’t be changed.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Orders have some special behavior on deletion"""

        # If the order is completed, it must not be deleted
        if self.__old_state == "COM":
            raise PermissionDenied("Completed orders can’t be deleted.")

        super().delete(*args, **kwargs)

    def __str__(self):
        if self.product:
            return "{} {} of {}".format(self.amount, self.product.unit, self.product)
        else:
            return "{} of {}".format(self.amount, self.product_suggestion)
