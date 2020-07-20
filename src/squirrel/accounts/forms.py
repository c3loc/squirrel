from crispy_forms.bootstrap import Field, FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Submit
from django import forms
from squirrel.accounts.models import Account, Transaction


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
            Field("purchase"),
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

        self.fields["purchase"].widget.attrs["size"] = "20"

    class Meta:
        model = Transaction
        fields = ["date", "amount", "description", "purchase", "account"]


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
