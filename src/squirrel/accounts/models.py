from datetime import date

from django.db import models
from djmoney.models.fields import MoneyField
from squirrel.orders.models import Purchase


class Account(models.Model):
    """ A bank account """

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """ A transaction on a bank account """

    class Meta:
        ordering = ["date", "id"]

    amount = MoneyField(max_digits=19, decimal_places=4, default_currency="EUR")

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    description = models.CharField(blank=True, null=True, max_length=1000)
    date = models.DateField(default=date.today)
    purchase = models.ForeignKey(
        Purchase, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.account}: {self.amount} - {self.description}"
