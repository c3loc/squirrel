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
from squirrel.orders.models import Pillage, Stockpile
from squirrel.util.views import get_form, post_form


@login_required
@permission_required("accounts.view_account", raise_exception=True)
def accounts(request):
    """ Renders a list of all accounts """
    return render(request, "accounts.html", {"accounts": Account.objects.all()})


@login_required
@permission_required("accounts.add_account", raise_exception=True)
def add_account(request):
    if request.method == "GET":
        return get_form(request, Account, AccountForm, None)

    if request.method == "POST":
        return post_form(request, Account, AccountForm, next_page="accounts:accounts")

    return HttpResponse(status=405)


@login_required
@permission_required("accounts.change_account", raise_exception=True)
def change_account(request, account_id):
    if request.method == "GET":
        return get_form(request, Account, AccountForm, account_id)

    if request.method == "POST":
        return post_form(
            request, Account, AccountForm, account_id, next_page="accounts:accounts"
        )

    return HttpResponse(status=405)


@login_required
@permission_required("accounts.edit_transaction", raise_exception=True)
def change_transaction(request, transaction_id):
    if request.method == "GET":
        return get_form(request, Transaction, TransactionForm, transaction_id)

    if request.method == "POST":
        return post_form(
            request,
            Transaction,
            TransactionForm,
            transaction_id,
            next_page="accounts:accounts",
        )

    return HttpResponse(status=405)


@login_required
@permission_required("accounts.delete_account", raise_exception=True)
def delete_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    account.delete()
    return redirect("accounts:accounts")


@login_required
@permission_required("accounts.delete_transaction", raise_exception=True)
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    transaction.delete()
    return redirect("accounts:accounts")


@login_required
@permission_required("accounts.add_transaction", raise_exception=True)
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
            # The regex removes all non-decmial characters.
            # Withdrawals are negative amounts and therefore multiplied by -1
            amount = (
                Money(sub(r"[^\d.]", "", row["Withdrawal"]), currency="EUR") * -1
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


@login_required
@permission_required("accounts.view_transaction", raise_exception=True)
def export_transaction_csv(request, account_id):
    """Exports all transactions with related orders as csv
    """

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="squirrel-transaction-export.csv"'

    field_names = ["Date", "Description", "Transfer", "Deposit", "Withdrawal"]

    lines = [field_names]

    for transaction in Transaction.objects.filter(account=account_id):

        lines.append(
            [
                transaction.date,
                transaction.description,
                "",  # Transfer is always empty
                transaction.amount
                if not transaction.amount < Money(0, currency="EUR")
                else "",
                transaction.amount
                if transaction.amount < Money(0, currency="EUR")
                else "",
            ]
        )

        # If the transaction is a Deposit, continue - nobody pays for deposits
        if not transaction.amount < Money(0, currency="EUR"):
            continue

        # for related orders with purchase/stockpile
        team_amount = {}

        for purchase in transaction.purchases.all():
            stockpiles = Stockpile.objects.filter(purchase=purchase)

            for stockpile in stockpiles:
                for pillage in Pillage.objects.filter(stockpile=stockpile):
                    if pillage.order.team in team_amount:
                        old_amount = team_amount[pillage.order.team]
                    else:
                        old_amount = Money(0, currency="EUR")

                    team_amount[pillage.order.team] = (
                        old_amount
                        + Money(
                            pillage.amount
                            * pillage.stockpile.unit_price.amount
                            * pillage.stockpile.tax
                            * (100 - purchase.rebate)
                            / 100,
                            currency="EUR",
                        )
                        if pillage.stockpile.purchase.is_net
                        else Money(
                            pillage.amount
                            * pillage.stockpile.unit_price.amount
                            * (100 - purchase.rebate)
                            / 100,
                            currency="EUR",
                        )
                    )

        for team, amount in team_amount.items():
            lines.append(
                [
                    "",  # Date
                    team,  # Description
                    "",  # Transfer
                    "",  # Deposit
                    amount * -1,
                ]
            )

    writer = csv.writer(response)
    for line in lines:
        writer.writerow(line)

    return response
