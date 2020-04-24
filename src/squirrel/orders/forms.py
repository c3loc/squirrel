from django import forms
from django.forms import ChoiceField, ModelChoiceField
from squirrel.orders.models import Event, Order, Product, Team, Vendor
from squirrel.orders.widgets import TextInput


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        my_teams = kwargs.pop("teams")
        my_states = kwargs.pop("states")
        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields["product"] = ModelChoiceField(
            to_field_name="name",
            queryset=Product.objects.all().order_by("name"),
            widget=TextInput(
                datalist=[p.name for p in Product.objects.all().order_by("name")],
                attrs={"autocomplete": "off"},
            ),
        )
        self.fields[
            "product"
        ].help_text = (
            "If you have more specific requirements, please add them as a comment."
        )

        self.fields["state"] = ChoiceField(choices=my_states)
        self.fields["team"] = ModelChoiceField(queryset=my_teams.order_by("name"))
        self.fields["event"].queryset = self.fields["event"].queryset.order_by("name")

    class Meta:
        model = Order
        fields = [
            "amount",
            "product",
            "comment",
            "state",
            "team",
            "event",
        ]

        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3, "cols": 30}),
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


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name"]
