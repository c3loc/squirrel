import csv
import datetime
from io import StringIO
from re import sub

from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from djmoney.money import Money
from squirrel.accounts.forms import AccountForm, ImportTransactionsForm, TransactionForm
from squirrel.accounts.models import Account, Transaction
from squirrel.util.views import get_form, post_form


@login_required
@permission_required("accounts.view_account", raise_exception=True)
def accounts(request):
    return render(request, "accounts.html", {"accounts": Account.objects.all()})


@login_required
@permission_required("accounts.create_account", raise_exception=True)
def create_account(request):
    """Creates a new account"""
    if request.method == "GET":
        form = AccountForm()
        return render(request, "instance.html", {"form": form})

    if request.method == "POST":
        return post_form(request, Account, AccountForm)

    return HttpResponse(status=405)


@login_required
@permission_required("accounts.edit_account", raise_exception=True)
def edit_account(request, account_id):
    """Modifies an account"""
    if request.method == "GET":
        return get_form(request, Account, AccountForm, account_id)

    if request.method == "POST":
        return post_form(request, Account, AccountForm, account_id)

    return HttpResponse(status=405)


@login_required
@permission_required("accounts.edit_transaction", raise_exception=True)
def edit_transaction(request, transaction_id):
    """Modifies a transaction"""
    if request.method == "GET":
        return get_form(request, Transaction, TransactionForm, transaction_id)

    if request.method == "POST":
        return post_form(request, Transaction, TransactionForm, transaction_id)

    return HttpResponse(status=405)


@login_required
@permission_required("accounts.delete_account", raise_exception=True)
def delete_account(request, account_id):
    """Deletes an account"""
    account = get_object_or_404(Account, id=account_id)
    account.delete()
    return redirect("accounts:accounts")


@login_required
@permission_required("accounts.delete_transaction", raise_exception=True)
def delete_transaction(request, transaction_id):
    """Deletes a transaction"""
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    return redirect("accounts:accounts")


@login_required
@permission_required("accounts.create_transaction", raise_exception=True)
def import_transactions(request, account_id):
    """Imports transactions for a specific account"""
    if request.method == "GET":
        form = ImportTransactionsForm()
        return render(request, "instance.html", {"form": form})

    if request.method == "POST":
        print(request.FILES["csv"])
        csv_reader = csv.DictReader(
            StringIO(request.FILES["csv"].read().decode("utf-8")), delimiter="\t"
        )

        for row in csv_reader:
            # Set the amount to the withdrawn sum or the Deposit sum.
            # The regex removes all non-decmial characters
            amount = (
                Money(sub(r"[^\d.]", "", row["Withdrawal"]), currency="EUR")
                if row["Withdrawal"] != ""
                else Money(sub(r"[^\d.]", "", row["Deposit"]), currency="EUR")
            )

            # Parse the date in the DD.MM.YYYY format
            date = datetime.datetime.strptime(row["Date"], "%d.%m.%Y").date()

            Transaction.objects.create(
                account=Account.objects.get(id=account_id),
                amount=amount,
                description=row["Description"],
                date=date,
            )

        return redirect("accounts:accounts")

    return HttpResponse(status=405)
