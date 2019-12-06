from django import forms
from django.forms import ModelChoiceField

from .models import Order, Product, Team


class OrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.my_teams = kwargs.pop("teams")
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields["team"] = ModelChoiceField(queryset=self.my_teams)

    def clean_team(self):
        if Team.objects.get(name=self.cleaned_data["team"]) in self.my_teams:
            return self.cleaned_data["team"]
        raise forms.ValidationError("Team must be one of your Teams")

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
