from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2 import SingleTableView

from .forms import OrderForm, ProductForm, TeamForm
from .models import Event, Order, Product, Team
from .tables import BudgetTable, OrderTable, ProductTable, TeamTable


def login_redirect(request):
    return redirect("login")


def overview(request):
    return render(request, "overview.html")


class OrderListView(LoginRequiredMixin, SingleTableView):
    model = Order
    table_class = OrderTable
    template_name = "orders.html"


class ProductListView(LoginRequiredMixin, SingleTableView):
    model = Product
    table_class = ProductTable
    template_name = "products.html"


class TeamListView(LoginRequiredMixin, SingleTableView):
    model = Team
    table_class = TeamTable
    template_name = "teams.html"


class BudgetListView(LoginRequiredMixin, SingleTableView):
    model = Team
    table_class = BudgetTable
    template_name = "budgets.html"


@login_required
def order(request, order_id=None):
    user = User.objects.first()  # TODO: get the currently logged in user

    if order_id:
        order_object = get_object_or_404(Order, id=order_id)
    else:
        order_object = None

    if request.method == "POST":
        if order_object:
            # TODO: Check that user has rights to edit order
            form = OrderForm(request.POST, instance=order_object)
        else:
            form = OrderForm(request.POST)

        if form.is_valid():
            order_object = form.save(commit=False)
            if not order_id:
                order_object.created_by = user
            order_object.save()

            return redirect("orders")
    else:
        if order_object:
            form = OrderForm(instance=order_object)
        else:
            form = OrderForm()

    return render(
        request,
        "order.html",
        {"form": form, "teams": Team.objects.all(), "events": Event.objects.all()},
    )


@login_required
def delete_order(request, order_id=None):
    # TODO: Check that user has rights to delete order
    order_object = get_object_or_404(Order, id=order_id)
    order_object.delete()

    return redirect("orders")


@login_required
def product(request, product_id=None):
    user = User.objects.first()  # TODO: get the currently logged in user

    if product_id:
        product_object = get_object_or_404(Product, id=product_id)
    else:
        product_object = None

    if request.method == "POST":
        if product_object:
            # TODO: Check that user has rights to edit product
            form = ProductForm(request.POST, instance=product_object)
        else:
            form = ProductForm(request.POST)

        if form.is_valid():
            product_object = form.save(commit=False)
            if not product_id:
                product_object.created_by = user
            product_object.save()

            return redirect("products")
    else:
        if product_object:
            form = ProductForm(instance=product_object)
        else:
            form = ProductForm()

    return render(request, "product.html", {"form": form})


@login_required
def delete_product(request, product_id=None):
    # TODO: Check that user has rights to delete product
    product_object = get_object_or_404(Product, id=product_id)
    product_object.delete()

    return redirect("products")


@login_required
def team(request, team_id=None):
    user = User.objects.first()  # TODO: get the currently logged in user

    if team_id:
        team_object = get_object_or_404(Team, id=team_id)
    else:
        team_object = None

    if request.method == "POST":
        if team_object:
            # TODO: Check that user has rights to edit team
            form = TeamForm(request.POST, instance=team_object)
        else:
            form = TeamForm(request.POST)

        if form.is_valid():
            team_object = form.save(commit=False)
            if not team_id:
                team_object.created_by = user
            team_object.save()

            return redirect("teams")
    else:
        if team_object:
            form = TeamForm(instance=team_object)
        else:
            form = TeamForm()

    return render(request, "team.html", {"form": form})


@login_required
def delete_team(request, team_id=None):
    # TODO: Check that user has rights to delete product
    team_object = get_object_or_404(Team, id=team_id)
    team_object.delete()

    return redirect("teams")
