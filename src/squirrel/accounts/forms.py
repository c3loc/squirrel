from crispy_forms.bootstrap import Field, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django import forms
from djmoney.money import Money
from squirrel.accounts.models import Account, Transaction
from squirrel.orders.models import Purchase


class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field("name"),
            FormActions(
                Submit("submit", "Save", css_class="btn btn-success"),
                HTML(
                    """<a href="{% url "accounts:accounts" %}" class="btn btn-secondary">Cancel</a>"""
                ),
                HTML(
                    """
                    {% if form.instance.id %}<a href="{% url "accounts:delete_account" form.instance.id %}"
                    class="btn btn-outline-danger pull-right">Delete</a>{% endif %}
                    """
                ),
            ),
        )

    class Meta:
        model = Account
        fields = [
            "name",
        ]


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            Field("date"),
            Field("amount"),
            Field("description"),
            Field("purchases_suggestion"),
            Field("purchases"),
            Field("account"),
            FormActions(
                Submit("submit", "Save", css_class="btn btn-success"),
                HTML(
                    """<a href="{% url "accounts:accounts" %}" class="btn btn-secondary">Cancel</a>"""
                ),
                HTML(
                    """
                    {% if form.instance.id %}<a href="{% url "accounts:delete_transaction" form.instance.id %}"
                    class="btn btn-outline-danger pull-right">Delete</a>{% endif %}
                    """
                ),
            ),
        )

        self.fields["purchases"].widget.attrs["size"] = "20"

        # Get all purchases where the difference of the abs(gross sum) to the transaction amount is less than a cent
        self.purchases_suggestion_choices = ()
        purchases = Purchase.objects.all()
        for purchase in purchases:  # TODO: check Django money comparison accuracy
            if abs(self.instance.amount) - purchase.sum_gross <= Money(
                0.01, currency="EUR"
            ) and abs(self.instance.amount) - purchase.sum_gross >= Money(
                -0.01, currency="EUR"
            ):
                self.purchases_suggestion_choices += ((purchase.id, str(purchase)),)

        # Set the suggestion list to the purchases we found
        self.fields["purchases_suggestion"].choices = self.purchases_suggestion_choices

    class Meta:
        model = Transaction
        fields = ["date", "amount", "description", "purchases", "account"]

    purchases_suggestion = forms.MultipleChoiceField(
        help_text="This field only shows likely matching purchases. All purchases you select "
        "here are added to the saved purchases below.",
        required=False,
    )

    def save(self, *args, **kwargs):
        # Get the IDs from all purchases in the „purchases“ field. This is needed because the
        # Query to get the „purchases“ field is ordered and we can’t union queries with ORDER BY later on.
        ids = [purchase.id for purchase in self.cleaned_data["purchases"]]

        # Get all Purchases that are in the „purchases“ or „purchases_suggestion“ field and set
        # the actual field to that queryset before saving
        self.cleaned_data["purchases"] = Purchase.objects.filter(
            id__in=ids + self.cleaned_data["purchases_suggestion"]
        )

        return super().save(*args, **kwargs)


class ImportTransactionsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ImportTransactionsForm, self).__init__(*args, **kwargs)

        # Cripsy form settings
        self.helper = FormHelper(self)
        self.helper.layout = Layout(
            HTML(
                """<div class="alert alert-info" role="alert">
                 You need to upload a Unicode formatted csv file with at least the following columns designated
                 in the first row: Date, Description, Deposit, Withdrawal. Other columns will be ignored.
                 </div>
                 """
            ),
            Field("csv"),
            FormActions(
                Submit("submit", "Import", css_class="btn btn-success"),
                HTML(
                    """<a href="{% url "accounts:accounts" %}" class="btn btn-secondary">Cancel</a>"""
                ),
            ),
        )

    csv = forms.FileField(label="CSV")
