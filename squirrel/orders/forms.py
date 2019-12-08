from django import forms
from django.forms import ModelChoiceField

from .models import Order, Product, Team


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        my_teams = kwargs.pop("teams")
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields["team"] = ModelChoiceField(queryset=my_teams)

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
