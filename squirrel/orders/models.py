"""
Models for our orders
"""
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
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

    name = models.CharField(max_length=250, default=None)
    unit = models.CharField(max_length=20, default="Stück")

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

    @property
    def net(self):
        return sum([good.net for good in Good.objects.filter(purchase=self)])

    @property
    def gross(self):
        return sum([good.gross for good in Good.objects.filter(purchase=self)])

    @property
    def state(self):
        raise AssertionError(
            "A purchase_net can only transitively set the state of its orders."
        )

    @state.setter
    def state(self, state):
        """Set the state of all orders related to this purchase_net"""
        if state not in dict(Order.STATE_CHOICES):
            raise ValueError("You have to specify an existing state.")

        goods = Good.objects.filter(purchase=self)
        for good in goods:
            for order in Order.objects.filter(good=good):
                order.state = state
                order.save()


class Good(models.Model):
    name = models.CharField(max_length=255)
    unit_price = models.PositiveIntegerField(verbose_name="Unit price in 100th cent")
    unit = models.CharField(max_length=20, default="Stück")
    tax_rate = models.PositiveIntegerField(verbose_name="Tax rate in %", default=19)
    amount = models.IntegerField()
    purchase = models.ForeignKey(
        Purchase, on_delete=models.PROTECT, related_name="goods"
    )

    @property
    def net(self):
        if self.purchase.is_net:
            return self.amount * self.unit_price
        else:
            return self.amount * self.unit_price / (1 + self.tax_rate / 100)

    @property
    def gross(self):
        if self.purchase.is_net:
            return self.amount * self.unit_price * (1 + self.tax_rate / 100)
        else:
            return self.amount * self.unit_price

    def __str__(self):
        return "{} {} of {}".format(self.amount, self.unit, self.name)

    def clean(self):
        """We check that the purchased amount is at least the sum of orders. By doing so, we ensure to buy enough"""
        order_sum = sum([order.amount for order in Order.objects.filter(good=self.id)])

        if self.amount < order_sum:
            raise ValidationError(
                "The purchased amount must be at least {}, the sum of orders!".format(
                    order_sum
                )
            )


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

    __old_state = None

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.__old_state = self.state

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

    # Either a product or a free form item have to be specified
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, null=True, blank=True
    )
    product_suggestion = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)

    state = models.CharField(choices=STATE_CHOICES, default="REQ", max_length=30)
    unit_price = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    good = models.ForeignKey(
        Good, on_delete=models.PROTECT, related_name="orders", blank=True, null=True
    )

    event = models.ForeignKey(
        Event, on_delete=models.PROTECT, related_name="orders", blank=True, null=True
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

    def clean(self):
        """We need to check if either a product or a free form text are set"""
        if not self.product and not self.product_suggestion:
            raise ValidationError("An order must have either a product or an item set")
        elif self.product and self.product_suggestion:
            raise ValidationError("An order must not have a product and an item set")

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
