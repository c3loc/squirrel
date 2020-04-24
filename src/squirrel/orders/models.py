"""
Models for our orders
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


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

    name = models.CharField(max_length=250, default=None, unique=True)
    unit = models.CharField(max_length=20, null=True, blank=True)

    # Default price in 10th cents
    default_price = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    is_net = models.BooleanField(
        verbose_name="Do items of this purchase show the net sum (and not the gross sum)?",
        default=True,
    )
    paid = models.BooleanField(verbose_name="Is the purchase paid?", default=False)
    payment_method = models.CharField(max_length=255, blank=True)
    payer = models.CharField(
        verbose_name="Person who paid the invoice", max_length=255, blank=True
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT)

    ordered_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return "Purchase with {} @ {}".format(self.vendor, self.ordered_at.date())


class Order(models.Model):
    """A single order. Orders are always referenced to a team"""

    class Meta:
        permissions = [
            ("request_order", "Can request a order"),
            ("approve_order", "Can approve a order"),
            ("receive_order", "Can receive order"),
            ("complete_order", "Can complete order"),
            ("export_csv", "Can export all orders as CSV"),
            ("view_order_all_teams", "Can view orders for all teams"),
            ("add_order_all_teams", "Can add orders for all teams"),
            ("change_order_all_teams", "Can change orders for all teams"),
            ("delete_order_all_teams", "Can delete orders for all teams"),
        ]

    STATE_CHOICES = [
        ("REQ", "Requested"),  # User has requested Order
        (
            "APP",
            "Approved",
        ),  # Order was approved by purchase_net department and will be purchased
        (
            "REA",
            "Ready for pick-up",
        ),  # Order has been delivered (and commissioned if necessary)
        ("COM", "Completed"),  # Order has been picked up by the team
    ]

    amount = models.PositiveIntegerField(default=1)

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, to_field="name", null=True
    )

    state = models.CharField(choices=STATE_CHOICES, default="REQ", max_length=30)
    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="orders", null=True
    )
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name="orders")

    comment = models.CharField(max_length=1000, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    created_by = models.ForeignKey(
        User, null=True, related_name="orders", on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        User, null=True, related_name="orders_updates", on_delete=models.SET_NULL
    )

    def __str__(self):
        unit = f"{self.product.unit} " if self.product.unit else ""
        return "{} {} of {}".format(self.amount, unit, self.product)
