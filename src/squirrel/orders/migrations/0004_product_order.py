# Generated by Django 3.0.7 on 2020-06-21 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_stockpile_unit_price_help"),
    ]

    operations = [
        migrations.AlterModelOptions(name="product", options={"ordering": ["name"]},),
    ]
