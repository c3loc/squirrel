"""
The URL routing for our project
"""
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path


def login_redirect(request):
    return redirect("login")


def orders_redirect(request):
    return redirect("orders:orders")


urlpatterns = [
    path("", orders_redirect),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "login", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path(
        "change",
        auth_views.PasswordChangeView.as_view(success_url="orders:orders"),
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
    path("admin/", admin.site.urls),
    path("orders/", include("squirrel.orders.urls", namespace="orders")),
    path("accounts/login/", login_redirect),
    path("accounts/", include("squirrel.accounts.urls", namespace="accounts")),
]
