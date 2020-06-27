"""
The URL routing for our project
"""
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from .orders import views

urlpatterns = [
    path("", views.orders_redirect),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "login", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path(
        "change",
        auth_views.PasswordChangeView.as_view(success_url="orders"),
        name="password_change",
    ),
    path(
        "change/done",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path("reset", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/done",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/complete",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("orders", views.OrderListView.as_view(), name="orders"),
    path("orders/new", views.order, name="new_order"),
    path("orders/<int:order_id>", views.order, name="edit_order"),
    path("orders/delete/<int:order_id>", views.delete_order, name="delete_order"),
    path("orders/export", views.export_orders_csv, name="export_orders_csv"),
    path("products", views.ProductListView.as_view(), name="products"),
    path("products/new", views.product, name="new_product"),
    path("products/<int:product_id>", views.product, name="edit_product"),
    path(
        "products/delete/<int:product_id>", views.delete_product, name="delete_product"
    ),
    path("vendors", views.VendorListView.as_view(), name="vendors"),
    path("vendors/new", views.vendor, name="new_vendor"),
    path("vendors/<int:vendor_id>", views.vendor, name="edit_vendor"),
    path("vendors/delete/<int:vendor_id>", views.delete_vendor, name="delete_vendor"),
    path("teams", views.TeamListView.as_view(), name="teams"),
    path("teams/new", views.team, name="new_team"),
    path("teams/<int:team_id>", views.team, name="edit_team"),
    path("teams/delete/<int:team_id>", views.delete_team, name="delete_team"),
    path("events", views.EventListView.as_view(), name="events"),
    path("events/new", views.event, name="new_event"),
    path("events/<int:event_id>", views.event, name="edit_event"),
    path("events/delete/<int:event_id>", views.delete_event, name="delete_event"),
    path("purchases", views.PurchaseListView.as_view(), name="purchases"),
    path("purchases/new", views.purchase, name="new_purchase"),
    path("purchases/<int:purchase_id>", views.purchase, name="edit_purchase"),
    path(
        "purchases/delete/<int:purchase_id>",
        views.delete_purchase,
        name="delete_purchase",
    ),
    path("stockpiles", views.StockpileListView.as_view(), name="stockpiles"),
    path("stockpiles/new", views.stockpile, name="new_stockpile"),
    path("stockpiles/<int:stockpile_id>", views.stockpile, name="edit_stockpile"),
    path(
        "stockpiles/delete/<int:stockpile_id>",
        views.delete_stockpile,
        name="delete_stockpile",
    ),
    path("pillages", views.PillageListView.as_view(), name="pillages"),
    path("pillages/new", views.pillage, name="new_pillage"),
    path("pillages/<int:pillage_id>", views.pillage, name="edit_pillage"),
    path(
        "pillages/delete/<int:pillage_id>", views.delete_pillage, name="delete_pillage",
    ),
    path("admin/", admin.site.urls),
    path("accounts/", include("squirrel.accounts.urls", namespace="account")),
]
