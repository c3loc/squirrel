from django.urls import path
from squirrel.accounts import views

app_name = "accounts"

urlpatterns = [
    path("accounts", views.accounts, name="accounts"),
    path("accounts/new", views.create_account, name="create_account"),
    path("accounts/<int:account_id>", views.edit_account, name="edit_account"),
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
        views.edit_transaction,
        name="edit_transaction",
    ),
    path(
        "transactions/<int:transaction_id>/delete",
        views.delete_transaction,
        name="delete_transaction",
    ),
]
