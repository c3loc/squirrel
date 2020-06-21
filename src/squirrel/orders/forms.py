from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.forms import ChoiceField, ModelChoiceField, inlineformset_factory
from squirrel.orders.models import (
    Event,
    Order,
    Pillage,
    Product,
    Purchase,
    Stockpile,
    Team,
    Vendor,
)
from squirrel.orders.widgets import TextInput


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        my_teams = kwargs.pop("teams")
        my_states = kwargs.pop("states")
        super(OrderForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset("Item", "amount", Field("product", autocomplete="off"), "comment"),
            Fieldset("Metadata", "state", "team", "event"),
            Submit("submit", "Save order", css_class="btn-success"),
        )

        self.fields["product"] = ModelChoiceField(
            queryset=Product.objects.all().order_by("name"),
            to_field_name="name",
            widget=TextInput(datalist=[p.name for p in Product.objects.all()]),
        )

        self.fields[
            "product"
        ].help_text = (
            "If you have more specific requirements, please add them as a comment."
        )

        self.fields["state"] = ChoiceField(choices=my_states)
        self.fields["team"] = ModelChoiceField(queryset=my_teams.order_by("name"))
        self.fields["event"].queryset = Event.objects.all().order_by("-id")

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
        fields = ["name", "unit", "default_price"]


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


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            "is_net",
            "paid",
            "payment_method",
            "payer",
            "vendor",
            "ordered_at",
            "paid_at",
        ]


class StockpileForm(forms.ModelForm):
    class Meta:
        model = Stockpile
        fields = ["product", "amount", "unit_price", "tax", "purchase"]


StockpileFormSet = inlineformset_factory(
    Purchase,
    Stockpile,
    fields=["product", "amount", "unit_price", "tax", "id"],
    extra=1,
)


class PillageForm(forms.ModelForm):
    class Meta:
        model = Pillage
        fields = ["amount", "stockpile", "order"]
