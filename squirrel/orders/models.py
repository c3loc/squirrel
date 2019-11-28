"""
Models for our orders
"""
from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product"""

    name = models.CharField(max_length=250)
    unit = models.CharField(max_length=20, default="pieces")
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, default=1.0000)
    url = models.URLField(blank=True)

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

    STATE_CHOICES = [
        ("REQ", "Requested"),  # User has requested Order
        ("APP", "Approved"),  # Order was approved by purchase department
        ("DEL", "Delivered"),  # Order has been delivered and commissioned
        ("COM", "Completed"),  # Order has been picked up and
    ]

    amount = models.PositiveIntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)
    state = models.CharField(choices=STATE_CHOICES, default="REQ", max_length=30)
    unit_price = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=4
    )

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

    def __str__(self):
        return "{} {} of {}".format(self.amount, self.product.unit, self.product)
