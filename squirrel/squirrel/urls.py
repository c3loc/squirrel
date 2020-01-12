"""
The URL routing for our project
"""
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from orders import views
from orders.api import resources
from tastypie.api import Api

v1_api = Api(api_name="v1")
v1_api.register(resources.ProductResource())

urlpatterns = [
    path("api/", include(v1_api.urls)),
    path("", views.overview, name="overview"),
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
    path("budgets", views.BudgetListView.as_view(), name="budgets"),
    path("admin/", admin.site.urls),
    path("accounts/login/", views.login_redirect),
]
