""" This migration makes previously imported transactions have the correct sign:
    Withdrawals will have a negative sum, Deposits a positive one
"""

from django.db import migrations


def forwards_func(apps, schema_editor):
    Transaction = apps.get_model("accounts", "transaction")

    for t in Transaction.objects.all():
        t.amount = t.amount * -1
        t.save()


def reverse_func(apps, schema_editor):
    Transaction = apps.get_model("accounts", "transaction")

    for t in Transaction.objects.all():
        t.amount = t.amount * -1
        t.save()


class Migration(migrations.Migration):

    dependencies = [("accounts", "0001_initial")]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]
