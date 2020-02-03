import csv

from decouple import UndefinedValueError, config
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2 import SingleTableView

from .forms import OrderForm, ProductForm, TeamForm, VendorForm
from .models import Event, Order, Product, Team, Vendor
from .tables import BudgetTable, OrderTable, ProductTable, TeamTable, VendorTable


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


class VendorListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_vendor"
    model = Vendor
    table_class = VendorTable
    template_name = "vendors.html"


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


# Not a View.
def _state_helper(request, order_object):
    if order_object.state == "REQ":
        if request.user.has_perm("orders.change_order") or request.user.has_perm(
            "orders.approve_order"
        ):
            my_states = [("REQ", "Requested"), ("APP", "Approved")]
        else:
            my_states = [("REQ", "Requested")]
    elif order_object.state == "APP":
        if request.user.has_perm("orders.change_order") or request.user.has_perm(
            "orders.receive_order"
        ):
            my_states = [("APP", "Approved"), ("REA", "Ready for pick-up")]
        else:
            my_states = [("APP", "Approved")]
    elif order_object.state == "REA":
        if request.user.has_perm("orders.change_order") or request.user.has_perm(
            "orders.complete_order"
        ):
            my_states = [("REA", "Ready for pick-up"), ("COM", "Completed")]
        else:
            my_states = [("REA", "Ready for pick-up")]
    else:  # order_object.state is COM
        my_states = [("COM", "Completed")]
    return my_states


@login_required
def order(request, order_id=None):
    if order_id:
        order_object = get_object_or_404(Order, id=order_id)
    else:
        order_object = None

    # limit team field
    if request.user.has_perm("orders.view_team"):
        my_teams = Team.objects.all()
    else:
        my_teams = Team.objects.filter(members=request.user)

    if request.method == "POST":
        if order_object:
            if request.user.has_perm("orders.change_order"):
                # can do almost anything
                form = OrderForm(
                    request.POST,
                    instance=order_object,
                    teams=my_teams,
                    states=Order.STATE_CHOICES,
                )
            elif (
                (
                    request.user.has_perm("orders.approve_order")
                    and order_object.state == "REQ"
                )
                or (
                    request.user.has_perm("orders.receive_order")
                    and order_object.state == "APP"
                )
                or (
                    request.user.has_perm("orders.complete_order")
                    and order_object.state == "REA"
                )
            ):
                form = OrderForm(
                    request.POST,
                    instance=order_object,
                    teams=my_teams,
                    states=_state_helper(request, order_object),
                )
            elif (
                request.user in order_object.team.members.all()
                and order_object.state == "REQ"
            ):
                form = OrderForm(
                    request.POST,
                    instance=order_object,
                    teams=my_teams,
                    states=[("REQ", "Requested")],
                )
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_order"):
                form = OrderForm(
                    request.POST, teams=my_teams, states=Order.STATE_CHOICES
                )
            elif request.user.has_perm("orders.request_order"):
                form = OrderForm(
                    request.POST, teams=my_teams, states=[("REQ", "Requested")]
                )
            else:
                raise PermissionDenied

        if form.is_valid():
            order_object = form.save(commit=False)
            if not order_id:
                order_object.created_by = request.user
            order_object.save()

            return redirect("orders")
    else:
        if order_object:
            # view a existing order

            if (
                request.user.has_perm("orders.view_order")
                or request.user in order_object.team.members.all()
            ):
                # limit the states
                my_states = _state_helper(request, order_object)

                if request.user.has_perm("orders.add_order"):
                    form = OrderForm(
                        instance=order_object, teams=my_teams, states=my_states
                    )
            else:
                raise PermissionDenied
        else:
            # new order form

            # preset the event field
            try:
                my_event = Event.objects.get(name=config("DEFAULT_ORDER_EVENT"))
            except (ObjectDoesNotExist, UndefinedValueError):
                # if nothing is set we use the latest Event object
                my_event = Event.objects.last()

            # preset the team field if we only have a singel team
            if my_teams.count() == 1:
                my_team = my_teams.first()
            else:
                my_team = Team.objects.none()

            # if we have the add_order perm, we can add in any state (admins)
            if request.user.has_perm("orders.add_order"):
                my_states = Order.STATE_CHOICES
            # if we have the request_order, we can only REQuest new orders
            elif request.user.has_perm("orders.request_order"):
                my_states = [("REQ", "Requested")]
            # we are not allowed to add a order
            else:
                raise PermissionDenied

            form = OrderForm(
                initial={
                    "event": my_event,
                    "state": ("REQ", "Requested"),
                    "team": my_team,
                },
                teams=my_teams,
                states=my_states,
            )

    return render(request, "order.html", {"form": form, "events": Event.objects.all()},)


@login_required
@permission_required("orders.delete_order", raise_exception=True)
def delete_order(request, order_id=None):
    order_object = get_object_or_404(Order, id=order_id)
    if (
        request.user.has_perm("orders.delete_order")
        and request.user in order_object.team.members.all()
        and order_object.state == "REQ"
    ) or request.user.has_perm("orders.delete_order_all_teams"):
        order_object.delete()
    else:
        raise PermissionDenied

    return redirect("orders")


@login_required
def vendor(request, vendor_id=None):
    if vendor_id:
        vendor_object = get_object_or_404(Vendor, id=vendor_id)
    else:
        vendor_object = None

    if request.method == "POST":
        if vendor_object:
            if request.user.has_perm("orders.change_vendor"):
                form = VendorForm(request.POST, instance=vendor_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_vendor"):
                form = VendorForm(request.POST)
            else:
                raise PermissionDenied

        if form.is_valid():
            vendor_object = form.save()
            return redirect("vendors")
    else:
        if vendor_object:
            if request.user.has_perm("orders.view_vendor"):
                form = VendorForm(instance=vendor_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_vendor"):
                form = VendorForm()
            else:
                raise PermissionDenied

    return render(request, "vendor.html", {"form": form, "events": Event.objects.all()})


@login_required
@permission_required("orders.delete_vendor", raise_exception=True)
def delete_vendor(request, vendor_id=None):
    vendor_object = get_object_or_404(Vendor, id=vendor_id)
    vendor_object.delete()

    return redirect("vendors")


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


@login_required
@permission_required("orders.export_csv", raise_exception=True)
def export_orders_csv(request):
    # TODO: This whole view needs to be reworked once we have updated the product/product suggestion thing
    if request.user.has_perm("orders.view_order"):
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(team__members=request.user)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="squirrel-export.csv"'

    # Get the names of the model fields
    field_names = [
        "Amount",
        "Item",
        "URL",
        "State",
        "Unit price",
        "Total price",
        "Event",
        "Team",
    ]

    lines = [field_names]

    for order_instance in orders:
        if order_instance.product:
            item = order_instance.product
        else:
            item = order_instance.product_suggestion

        total_price = order_instance.unit_price * order_instance.amount

        lines.append(
            [
                order_instance.amount,
                item,
                order_instance.url,
                order_instance.get_state_display(),
                order_instance.unit_price,
                total_price,
                order_instance.event,
                order_instance.team,
            ]
        )

    writer = csv.writer(response)
    for line in lines:
        writer.writerow(line)

    return response
