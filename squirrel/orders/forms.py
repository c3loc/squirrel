from django import forms
from django.forms import ModelChoiceField

from .models import Order, Product, Team, Vendor


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        my_teams = kwargs.pop("teams")
        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields["team"] = ModelChoiceField(queryset=my_teams.order_by("name"))
        self.fields["product"].queryset = self.fields["product"].queryset.order_by(
            "name"
        )
        self.fields["event"].queryset = self.fields["event"].queryset.order_by("name")

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
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields["vendor"].queryset = self.fields["vendor"].queryset.order_by("name")

    class Meta:
        model = Product
        fields = ["name", "unit", "unit_price", "url", "vendor"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["name"]
