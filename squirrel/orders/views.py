from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
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

    def get_table_data(self):
        if self.request.user.has_perm("orders.view_order"):
            return Order.objects.all()
        else:
            return Order.objects.filter(team__members=self.request.user)


class ProductListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_product"
    model = Product
    table_class = ProductTable
    template_name = "products.html"


class TeamListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_team"
    model = Team
    table_class = TeamTable
    template_name = "teams.html"


class BudgetListView(LoginRequiredMixin, SingleTableView):
    model = Team
    table_class = BudgetTable
    template_name = "budgets.html"

    def get_table_data(self):
        if self.request.user.has_perm("orders.view_budget"):
            return Team.objects.all()
        else:
            return Team.objects.filter(members=self.request.user)


@login_required
def order(request, order_id=None):
    if order_id:
        order_object = get_object_or_404(Order, id=order_id)
    else:
        order_object = None

    if request.user.has_perm("orders.view_team"):
        my_teams = Team.objects.all()
    else:
        my_teams = Team.objects.filter(members=request.user)

    if request.method == "POST":
        if order_object:
            # TODO: Check that user has rights to edit order
            form = OrderForm(request.POST, instance=order_object, teams=my_teams)
        else:
            form = OrderForm(request.POST, teams=my_teams)

        if form.is_valid():
            order_object = form.save(commit=False)
            if not order_id:
                order_object.created_by = request.user
            order_object.save()

            return redirect("orders")
    else:
        if order_object:
            form = OrderForm(instance=order_object, teams=my_teams)
        else:
            form = OrderForm(teams=my_teams)

    return render(request, "order.html", {"form": form, "events": Event.objects.all()},)


@login_required
def delete_order(request, order_id=None):
    # TODO: Check that user has rights to delete order
    order_object = get_object_or_404(Order, id=order_id)
    order_object.delete()

    return redirect("orders")


@login_required
@permission_required("orders.view_product", raise_exception=True)
def product(request, product_id=None):
    if product_id:
        product_object = get_object_or_404(Product, id=product_id)
    else:
        product_object = None

    if request.method == "POST":
        if product_object:
            if request.user.has_perm("orders.change_product"):
                form = ProductForm(request.POST, instance=product_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_product"):
                form = ProductForm(request.POST)
            else:
                raise PermissionDenied

        if form.is_valid():
            form.save()
            return redirect("products")
    else:
        if product_object:
            form = ProductForm(instance=product_object)
        else:
            form = ProductForm()

    return render(request, "product.html", {"form": form})


@login_required
@permission_required("orders.delete_product", raise_exception=True)
def delete_product(request, product_id=None):
    product_object = get_object_or_404(Product, id=product_id)
    product_object.delete()

    return redirect("products")


@login_required
@permission_required("orders.view_team", raise_exception=True)
def team(request, team_id=None):
    if team_id:
        team_object = get_object_or_404(Team, id=team_id)
    else:
        team_object = None

    if request.method == "POST":
        if team_object:
            if request.user.has_perm("orders.change_team"):
                form = TeamForm(request.POST, instance=team_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_team"):
                form = TeamForm(request.POST)
            else:
                raise PermissionDenied

        if form.is_valid():
            form.save()
            return redirect("teams")
    else:
        if team_object:
            form = TeamForm(instance=team_object)
        else:
            form = TeamForm()

    return render(request, "team.html", {"form": form})


@login_required
@permission_required("orders.delete_team", raise_exception=True)
def delete_team(request, team_id=None):
    team_object = get_object_or_404(Team, id=team_id)
    team_object.delete()

    return redirect("teams")
