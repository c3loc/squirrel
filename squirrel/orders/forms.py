from django import forms

from .models import Order, Product, Team


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "amount",
            "product",
            "product_suggestion",
            "url",
            "state",
            "unit_price",
            "event",
            "team",
        ]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "unit", "unit_price", "url"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]
