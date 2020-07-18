"""
Models for our orders
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from djmoney.models.fields import MoneyField


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

    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=250, default=None, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """A product that can be ordered"""

    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=250, default=None, unique=True)
    unit = models.CharField(max_length=20, null=True, blank=True)
    default_price = MoneyField(
        max_digits=19, decimal_places=4, default_currency="EUR", null=True, blank=True
    )

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

    @property
    def sum_net(self):
        """ The sum of the purchase in €, net """
        if self.is_net:
            return self.__sum_without_tax_adjustment()

        # Sum over all purchase sums and cost items, divide each by its tax
        sums = [
            Stockpile.objects.filter(purchase=self).aggregate(
                total=Sum(
                    F("amount") * F("unit_price") / F("tax"), output_field=MoneyField(),
                )
            )["total"],
            CostItem.objects.filter(purchase=self).aggregate(
                total=Sum(
                    F("amount") * F("unit_price") / F("tax"), output_field=MoneyField(),
                )
            )["total"],
        ]

        return sum([item for item in sums if item is not None])

    @property
    def sum_gross(self):
        """ The sum of the purchase in €, gross"""
        if self.is_net:
            # Sum over all purchase sums and cost items, multiply each with its tax
            sums = [
                Stockpile.objects.filter(purchase=self).aggregate(
                    total=Sum(
                        F("amount") * F("unit_price") * F("tax"),
                        output_field=MoneyField(),
                    )
                )["total"],
                CostItem.objects.filter(purchase=self).aggregate(
                    total=Sum(
                        F("amount") * F("unit_price") * F("tax"),
                        output_field=MoneyField(),
                    )
                )["total"],
            ]
            return sum([item for item in sums if item is not None])

        return self.__sum_without_tax_adjustment()

    def __sum_without_tax_adjustment(self):
        """ Returns the sum of all stockpiles and cost items without adding or subtracting tax"""
        sums = [
            Stockpile.objects.filter(purchase=self).aggregate(
                total=Sum(F("amount") * F("unit_price"), output_field=MoneyField())
            )["total"],
            CostItem.objects.filter(purchase=self).aggregate(
                total=Sum(F("amount") * F("unit_price"), output_field=MoneyField())
            )["total"],
        ]

        return sum([item for item in sums if item is not None])

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
        Product,
        on_delete=models.PROTECT,
        null=True,
        help_text="If you have more specific requirements, please add them as a comment.",
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

    @property
    def to_pillage(self):
        """ The amount of the order that has yet to be pillaged """
        return self.amount - (
            (self.pillage_set.all().aggregate(Sum("amount"))["amount__sum"] or 0)
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.to_pillage > 0:
            product_stockpiles = Stockpile.objects.filter(product=self.product)

            with_stock = [s for s in product_stockpiles if s.stock > 0]

            while self.to_pillage > 0 and len(with_stock) > 0:
                stockpile = with_stock.pop(0)
                Pillage.objects.create(
                    order=self,
                    stockpile=stockpile,
                    amount=min(self.to_pillage, stockpile.stock),
                )


class Stockpile(models.Model):
    """
    A stockpile is a specific amount of a product that has been bought at a certain price.
    It can then be pillaged by orders.
    """

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    unit_price = MoneyField(max_digits=19, decimal_places=4, default_currency="EUR")

    """
    A stockpile may belong to a purchase, but does not have to be. Surprisingly often, you will just find things in
    your storage.
    """
    purchase = models.ForeignKey(
        Purchase, on_delete=models.CASCADE, null=True, blank=True
    )

    # The tax rate for the stockpile as a factor
    tax = models.FloatField(
        verbose_name="Tax rate", help_text="The tax rate as a factor of the net price"
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

    def __init__(self, *args, **kwargs):
        super(Stockpile, self).__init__(*args, **kwargs)
        try:
            self.inital_product = self.product
        except Product.DoesNotExist:
            self.inital_product = None

    def clean(self):
        if self.inital_product and (self.product != self.inital_product):
            raise ValidationError("You can’t change the product of a Stockpile!")

    def save(self, *args, **kwargs):
        """
        As save does not call full_clean, we call clean explicitly
        """
        self.clean()
        super().save(*args, **kwargs)

        # While there is stock, create pillages for orders that are not topped up yet
        # TODO: We start with which orders? Possible:
        # * oldest (id)
        # * smallest
        # * largest

        # Get all orders for the product
        orders = Order.objects.filter(product=self.product)

        # Filter for orders that still need something
        to_fill = [o for o in orders if o.to_pillage > 0]

        while self.stock > 0 and len(to_fill) > 0:
            order = to_fill.pop(0)
            Pillage.objects.create(
                order=order, stockpile=self, amount=min(self.stock, order.to_pillage),
            )


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
        pillaged = self.order.amount - self.order.to_pillage

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


class CostItem(models.Model):
    """
    A CostItem is something that costs us additional money, but does not yield a good.
    E.g. shipping costs etc.

    The sum of all cost items is equally divided to all pillages of stockpiles from this purchase.
    """

    description = models.CharField(max_length=250)
    amount = models.PositiveIntegerField()
    unit_price = MoneyField(max_digits=19, decimal_places=4, default_currency="EUR")

    # All CostItems belong to a purchase
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)

    # The tax rate for the stockpile as a factor
    tax = models.FloatField(
        verbose_name="Tax rate", help_text="The tax rate as a factor of the net price"
    )

    def __str__(self):
        return f"Extra cost of {self.description} for {self.purchase}"
