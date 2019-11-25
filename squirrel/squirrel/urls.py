"""
The URL routing for our project
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from orders import views

urlpatterns = [
    path("", views.overview, name="overview"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "login", auth_views.LoginView.as_view(template_name="login.html"), name="login"
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
    path("products", views.ProductListView.as_view(), name="products"),
    path("products/new", views.product, name="new_product"),
    path("products/<int:product_id>", views.product, name="edit_product"),
    path(
        "products/delete/<int:product_id>", views.delete_product, name="delete_product"
    ),
    path("admin/", admin.site.urls),
    path("accounts/login/", views.login_redirect),
]
