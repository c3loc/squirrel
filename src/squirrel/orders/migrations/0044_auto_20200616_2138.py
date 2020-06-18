# Generated by Django 3.0.7 on 2020-06-16 21:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0043_auto_20200614_2214"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pillage",
            name="amount",
            field=models.PositiveIntegerField(
                validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
    ]