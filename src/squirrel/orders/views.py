import csv

from decouple import UndefinedValueError, config
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django_tables2 import SingleTableView
from squirrel.orders.forms import (
    EventForm,
    OrderForm,
    PillageForm,
    ProductForm,
    PurchaseForm,
    StockpileForm,
    StockpileFormSet,
    TeamForm,
    VendorForm,
)
from squirrel.orders.models import (
    Event,
    Order,
    Pillage,
    Product,
    Purchase,
    Stockpile,
    Team,
    Vendor,
)
from squirrel.orders.tables import (
    EventTable,
    OrderTable,
    PillageTable,
    ProductTable,
    PurchaseTable,
    StockpileTable,
    TeamTable,
    VendorTable,
)


def login_redirect(request):
    return redirect("login")


def orders_redirect(request):
    return redirect("orders")


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


class EventListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_event"
    model = Event
    table_class = EventTable
    template_name = "events.html"


class PurchaseListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_purchase"
    model = Purchase
    table_class = PurchaseTable
    template_name = "purchases.html"


class StockpileListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_stockpile"
    model = Stockpile
    table_class = StockpileTable
    template_name = "stockpiles.html"


class PillageListView(PermissionRequiredMixin, SingleTableView):
    permission_required = "orders.view_pillage"
    model = Pillage
    table_class = PillageTable
    template_name = "pillages.html"


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

        # Create the product if it does not yet exist
        Product.objects.get_or_create(name=request.POST["product"])

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
                my_event = Event.objects.all().order_by("id").last()

            # preset the team field if we only have a single team
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

    return render(request, "order.html", {"form": form})


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
def event(request, event_id=None):
    if event_id:
        event_object = get_object_or_404(Event, id=event_id)
    else:
        event_object = None

    if request.method == "POST":
        if event_object:
            if request.user.has_perm("orders.change_event"):
                form = EventForm(request.POST, instance=event_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_event"):
                form = EventForm(request.POST)
            else:
                raise PermissionDenied

        if form.is_valid():
            form.save()
            return redirect("events")
    else:
        if event_object:
            if request.user.has_perm("orders.view_event"):
                form = EventForm(instance=event_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_event"):
                form = EventForm()
            else:
                raise PermissionDenied

    return render(request, "event.html", {"form": form})


@login_required
@permission_required("orders.delete_vendor", raise_exception=True)
def delete_event(request, event_id=None):
    event_object = get_object_or_404(Event, id=event_id)
    event_object.delete()

    return redirect("events")


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
        # TODO: Add prices back

        lines.append(
            [
                order_instance.amount,
                order_instance.product,
                order_instance.url,
                order_instance.get_state_display(),
                order_instance.event,
                order_instance.team,
            ]
        )

    writer = csv.writer(response)
    for line in lines:
        writer.writerow(line)

    return response


@login_required
@permission_required("orders.view_purchase", raise_exception=True)
def purchase(request, purchase_id=None):
    """
    View of a purchase
    """
    if purchase_id:
        purchase_object = get_object_or_404(Purchase, id=purchase_id)
    else:
        purchase_object = None

    if request.method == "POST":
        if purchase_object:
            if request.user.has_perm("orders.change_purchase"):
                form = PurchaseForm(request.POST, instance=purchase_object)
                formset = StockpileFormSet(request.POST, instance=form.instance)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_purchase"):
                form = PurchaseForm(request.POST)
                formset = StockpileFormSet(request.POST, instance=form.instance)
            else:
                raise PermissionDenied

        if form.is_valid() and formset.is_valid():
            p = form.save()
            formset.save()
            return redirect(f"/purchases/{p.id}")

    else:
        if purchase_object:
            form = PurchaseForm(instance=purchase_object)
            formset = StockpileFormSet(instance=Purchase.objects.get(id=purchase_id))

        else:
            form = PurchaseForm()
            formset = StockpileFormSet()

    # FIXME: I am sure this can be done better
    if purchase_object:
        sum_net = purchase_object.sum_net
        sum_gross = purchase_object.sum_gross
    else:
        sum_net = 0
        sum_gross = 0

    return render(
        request,
        "purchase.html",
        {"form": form, "formset": formset, "sum_net": sum_net, "sum_gross": sum_gross},
    )


@login_required
@permission_required("orders.delete_purchase", raise_exception=True)
def delete_purchase(request, purchase_id=None):
    purchase_object = get_object_or_404(Purchase, id=purchase_id)
    purchase_object.delete()

    return redirect("purchases")


@login_required
def stockpile(request, stockpile_id=None):
    if stockpile_id:
        stockpile_object = get_object_or_404(Stockpile, id=stockpile_id)
    else:
        stockpile_object = None

    if request.method == "POST":
        if stockpile_object:
            if request.user.has_perm("orders.change_stockpile"):
                form = StockpileForm(request.POST, instance=stockpile_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_stockpile"):
                form = StockpileForm(request.POST)
            else:
                raise PermissionDenied

        if form.is_valid():
            stockpile_object = form.save()
            return redirect("stockpiles")
    else:
        if stockpile_object:
            if request.user.has_perm("orders.view_stockpile"):
                form = StockpileForm(instance=stockpile_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_stockpile"):
                form = StockpileForm()
            else:
                raise PermissionDenied

    return render(
        request, "stockpile.html", {"form": form, "events": Event.objects.all()}
    )


@login_required
@permission_required("orders.delete_stockpile", raise_exception=True)
def delete_stockpile(request, stockpile_id=None):
    stockpile_object = get_object_or_404(Stockpile, id=stockpile_id)
    stockpile_object.delete()

    return redirect("stockpiles")


@login_required
def pillage(request, pillage_id=None):
    if pillage_id:
        pillage_object = get_object_or_404(Pillage, id=pillage_id)
    else:
        pillage_object = None

    if request.method == "POST":
        if pillage_object:
            if request.user.has_perm("orders.change_pillage"):
                form = PillageForm(request.POST, instance=pillage_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_pillage"):
                form = PillageForm(request.POST)
            else:
                raise PermissionDenied

        if form.is_valid():
            pillage_object = form.save()
            return redirect("pillages")
    else:
        if pillage_object:
            if request.user.has_perm("orders.view_pillage"):
                form = PillageForm(instance=pillage_object)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_pillage"):
                form = PillageForm()
            else:
                raise PermissionDenied

    return render(
        request, "pillage.html", {"form": form, "events": Event.objects.all()}
    )


@login_required
@permission_required("orders.delete_pillage", raise_exception=True)
def delete_pillage(request, pillage_id=None):
    pillage_object = get_object_or_404(Pillage, id=pillage_id)
    pillage_object.delete()

    return redirect("pillages")
