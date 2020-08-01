from django.urls import path
from squirrel.accounts import views

app_name = "accounts"

urlpatterns = [
    path("accounts", views.accounts, name="accounts"),
    path("accounts/add", views.add_account, name="add_account"),
    path("accounts/<int:account_id>", views.change_account, name="change_account"),
    path(
        "accounts/<int:account_id>/delete", views.delete_account, name="delete_account"
    ),
    path(
        "accounts/<int:account_id>/import-transactions",
        views.import_transactions,
        name="import_transactions",
    ),
    path(
        "transactions/<int:transaction_id>",
        views.change_transaction,
        name="change_transaction",
    ),
    path(
        "transactions/<int:transaction_id>/delete",
        views.delete_transaction,
        name="delete_transaction",
    ),
]
