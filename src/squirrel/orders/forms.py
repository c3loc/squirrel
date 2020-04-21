import floppyforms.__future__
from django import forms
from django.forms import ChoiceField, ModelChoiceField

from .models import Order, Product, Team, Vendor


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        my_teams = kwargs.pop("teams")
        my_states = kwargs.pop("states")
        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields["team"] = ModelChoiceField(queryset=my_teams.order_by("name"))
        self.fields["product"] = ModelChoiceField(
            to_field_name="name",
            queryset=Product.objects.all().order_by("name"),
            widget=floppyforms.__future__.TextInput(
                datalist=[p.name for p in Product.objects.all().order_by("name")],
                attrs={"autocomplete": "off"},
            ),
        )
        self.fields[
            "product"
        ].help_text = (
            "If you have more specific requirements, please add them as a comment."
        )
        self.fields["event"].queryset = self.fields["event"].queryset.order_by("name")
        self.fields["state"] = ChoiceField(choices=my_states)

    class Meta:
        model = Order
        fields = [
            "amount",
            "product",
            "url",
            "comment",
            "state",
            "unit_price",
            "event",
            "team",
        ]

        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4, "cols": 15}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "unit"]


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ["name"]
