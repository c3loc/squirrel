"""
Models for our orders
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
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
    is_net = models.BooleanField(verbose_name="Prices are net", default=True,)
    paid = models.BooleanField(help_text="Is the purchase paid?", default=False)
    payment_method = models.CharField(max_length=255, blank=True)
    payer = models.CharField(
        help_text="Person who paid the invoice", max_length=255, blank=True
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

    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True)

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


class Stockpile(models.Model):
    """
    A stockpile is a specific amount of a product that has been bought at a certain price.
    It can then be pillaged by orders.
    """

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()

    # Unit price in 10th cents
    unit_price = models.PositiveIntegerField()

    """
    A stockpile may belong to a purchase, but does not have to be. Surprisingly often, you will just find things in
    your storage.
    """
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def stock(self):
        """
        The stock is calculated by taking the total amount bought and subtracting the sum of pillages.
        :return: the number left in stock
        """

        pillages = self.pillage_set.all().aggregate(Sum("amount"))["amount__sum"]
        if pillages is None:
            pillages = 0

        return self.amount - pillages

    def __str__(self):
        return f"Stockpile of {self.product} ({self.stock}/{self.amount})"


class Pillage(models.Model):
    """
    A pillage is the connection between an order and a stockpile.

    It specifies how much an order has taken from a stockpile
    """

    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    stockpile = models.ForeignKey(Stockpile, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def clean(self):
        """
        We need to ensure that the product of the stockpile and the order match

        We also need to ensure that a pillage does not take more stock than available from our stockpile and that
        the order does not get more items than requested.
        """

        # Check that products of order and stockpile match
        if self.stockpile.product != self.order.product:
            raise ValidationError(
                "The product of the order and the stockpile it is taken from have to match!"
            )

        # Get how much is already pillaged for the order in other pillages
        pillaged = (
            self.order.pillage_set.filter(~Q(id=self.id)).aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )

        if self.amount + pillaged > self.order.amount:
            raise ValidationError(
                f"The order only is for {self.order.amount}. With this pillage of {self.amount}, "
                f"it would go to {self.amount + pillaged}."
            )

        if self.amount > self.stockpile.stock:
            raise ValidationError(
                f"The stockpile has {self.stockpile.stock} available, you requested {self.amount}."
            )

        super().clean()

    def save(self, *args, **kwargs):
        """
        As save does not call full_clean, we call clean explicitly
        """
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pillage of {self.amount} for {self.order} from {self.stockpile}"
