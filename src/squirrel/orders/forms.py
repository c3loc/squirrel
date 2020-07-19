from crispy_forms.bootstrap import Field, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django import forms
from django.forms import inlineformset_factory
from squirrel.orders.models import (
    CostItem,
    Event,
    Order,
    Pillage,
    Product,
    Purchase,
    Stockpile,
    Team,
    Vendor,
)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "amount",
            "product",
            "comment",
            "team",
            "event",
        ]

        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3, "cols": 30}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Fieldset(
                "Item",
                "amount",
                Field(
                    "product",
                    help_text="If you have more specific requirements, please add them as a comment.",
                ),
                "comment",
            ),
            Fieldset("Metadata", "team", "event"),
            FormActions(
                Submit("submit", "Save", css_class="btn btn-success"),
                HTML(
                    """<a href="{% url "orders:orders" %}" class="btn btn-secondary">Cancel</a>"""
                ),
                HTML(
                    """
                    {% if form.instance.id %}<a href="{% url "orders:delete_stockpile" form.instance.id %}"
                    class="btn btn-outline-danger pull-right">Delete</a>{% endif %}
                    """
                ),
            ),
        )


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
            "rebate",
        ]


class StockpileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StockpileForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field("product"),
            Field("amount"),
            Field("unit_price"),
            Field("tax"),
            Field("purchase"),
            FormActions(
                Submit("submit", "Save", css_class="btn btn-success"),
                HTML(
                    """<a href="{% url "orders:stockpiles" %}" class="btn btn-secondary">Cancel</a>"""
                ),
                HTML(
                    """
                    {% if form.instance.id %}<a href="{% url "orders:delete_stockpile" form.instance.id %}"
                    class="btn btn-outline-danger pull-right">Delete</a>{% endif %}
                    """
                ),
            ),
        )

    class Meta:
        model = Stockpile
        fields = [
            "product",
            "amount",
            "unit_price",
            "tax",
            "purchase",
        ]


StockpileFormSet = inlineformset_factory(
    Purchase,
    Stockpile,
    fields=["product", "amount", "unit_price", "tax", "id"],
    extra=1,
)


CostItemFormSet = inlineformset_factory(
    Purchase,
    CostItem,
    fields=["description", "amount", "unit_price", "tax", "id"],
    extra=1,
)


class PillageForm(forms.ModelForm):
    class Meta:
        model = Pillage
        fields = ["amount", "stockpile", "order"]

    def __init__(self, *args, **kwargs):
        super(PillageForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field("amount"),
            Field("order"),
            Field("stockpile"),
            FormActions(
                Submit("submit", "Save", css_class="btn btn-success"),
                HTML(
                    """<a href="{% url "orders:stockpiles" %}" class="btn btn-secondary">Cancel</a>"""
                ),
                HTML(
                    """
                    {% if form.instance.id %}<a href="{% url "orders:delete_pillage" form.instance.id %}"
                    class="btn btn-outline-danger pull-right">Delete</a>{% endif %}
                    """
                ),
            ),
        )
