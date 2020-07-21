import csv

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django_tables2 import SingleTableView
from djmoney.money import Money
from squirrel.orders.forms import (
    CostItemFormSet,
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
from squirrel.orders.tables import EventTable, ProductTable, TeamTable, VendorTable
from squirrel.util.views import get_form, post_form


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
            return redirect("orders:vendors")
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

    return redirect("orders:vendors")


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
            return redirect("orders:events")
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

    return redirect("orders:events")


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
            return redirect("orders:products")
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

    return redirect("orders:products")


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
            return redirect("orders:teams")
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

    return redirect("orders:teams")


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
                costitem_formset = CostItemFormSet(request.POST, instance=form.instance)
            else:
                raise PermissionDenied
        else:
            if request.user.has_perm("orders.add_purchase"):
                form = PurchaseForm(request.POST)
                formset = StockpileFormSet(request.POST, instance=form.instance)
                costitem_formset = CostItemFormSet(request.POST, instance=form.instance)
            else:
                raise PermissionDenied

        if form.is_valid() and formset.is_valid() and costitem_formset.is_valid():
            p = form.save()
            formset.save()
            costitem_formset.save()
            return redirect(reverse("orders:change_purchase", args=[p.id]))

    else:
        if purchase_object:
            form = PurchaseForm(instance=purchase_object)
            formset = StockpileFormSet(instance=Purchase.objects.get(id=purchase_id))
            costitem_formset = CostItemFormSet(
                instance=Purchase.objects.get(id=purchase_id)
            )

        else:
            form = PurchaseForm()
            formset = StockpileFormSet()
            costitem_formset = CostItemFormSet()

    # FIXME: I am sure this can be done better
    if purchase_object:
        sum_net = purchase_object.sum_net
        sum_gross = purchase_object.sum_gross
    else:
        sum_net = Money(0, currency="EUR")
        sum_gross = Money(0, currency="EUR")

    return render(
        request,
        "purchase.html",
        {
            "form": form,
            "formset": formset,
            "costitem_formset": costitem_formset,
            "sum_net": sum_net,
            "sum_gross": sum_gross,
        },
    )


@login_required
def change_pillage(request, pillage_id):
    if request.method == "GET":
        return get_form(request, Pillage, PillageForm, pillage_id)

    if request.method == "POST":
        return post_form(
            request, Pillage, PillageForm, pillage_id, next_page="orders:stockpiles"
        )


@login_required
@permission_required("orders.delete_pillage", raise_exception=True)
def delete_pillage(request, pillage_id=None):
    pillage_object = get_object_or_404(Pillage, id=pillage_id)
    pillage_object.delete()

    return redirect("orders:stockpiles")


@login_required
@permission_required("orders.view_stockpiles", raise_exception=True)
def stockpiles(request):
    """ Renders a list of all stockpiles """
    return render(request, "stockpiles.html", {"stockpiles": Stockpile.objects.all()})


@login_required
@permission_required("orders:create_stockpile", raise_exception=True)
def create_stockpile(request):
    if request.method == "GET":
        return get_form(request, Stockpile, StockpileForm, None)

    if request.method == "POST":
        return post_form(
            request, Stockpile, StockpileForm, next_page="orders:stockpiles"
        )

    return HttpResponse(status=405)


@login_required
@permission_required("orders:change_stockpile", raise_exception=True)
def change_stockpile(request, stockpile_id):
    if request.method == "GET":
        return get_form(request, Stockpile, StockpileForm, stockpile_id)

    if request.method == "POST":
        return post_form(
            request,
            Stockpile,
            StockpileForm,
            stockpile_id,
            next_page="orders:stockpiles",
        )

    return HttpResponse(status=405)


@login_required
@permission_required("orders.delete_stockpile", raise_exception=True)
def delete_stockpile(request, stockpile_id=None):
    stockpile_object = get_object_or_404(Stockpile, id=stockpile_id)
    stockpile_object.delete()

    return redirect("orders:stockpiles")


@login_required
@permission_required("orders.view_orders", raise_exception=True)
def orders(request):
    """ Renders a list of all orders """
    return render(request, "orders.html", {"orders": Order.objects.all()})


@login_required
@permission_required("orders:create_order", raise_exception=True)
def create_order(request):
    if request.method == "GET":
        return get_form(request, Order, OrderForm, None)

    if request.method == "POST":
        return post_form(request, Order, OrderForm, next_page="orders:orders")

    return HttpResponse(status=405)


@login_required
@permission_required("orders:change_order", raise_exception=True)
def change_order(request, order_id):
    if request.method == "GET":
        return get_form(request, Order, OrderForm, order_id)

    if request.method == "POST":
        return post_form(
            request, Order, OrderForm, order_id, next_page="orders:orders",
        )

    return HttpResponse(status=405)


@login_required
@permission_required("orders.delete_order", raise_exception=True)
def delete_order(request, order_id=None):
    order_object = get_object_or_404(Order, id=order_id)
    order_object.delete()

    return redirect("orders:orders")


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
                order_instance.event,
                order_instance.team,
            ]
        )

    writer = csv.writer(response)
    for line in lines:
        writer.writerow(line)

    return response


@login_required
@permission_required("orders.view_purchases", raise_exception=True)
def purchases(request):
    """ Renders a list of all purchases """
    return render(request, "purchases.html", {"purchases": Purchase.objects.all()})


# @login_required
# @permission_required("orders:create_purchase", raise_exception=True)
# def create_purchase(request):
#     if request.method == "GET":
#         return get_form(request, Purchase, PurchaseForm, None)

#     if request.method == "POST":
#         return post_form(request, Purchase, PurchaseForm, next_page="orders:purchases")

#     return HttpResponse(status=405)


# @login_required
# @permission_required("orders:change_purchase", raise_exception=True)
# def change_purchase(request, purchase_id):
#     if request.method == "GET":
#         return get_form(request, Purchase, PurchaseForm, purchase_id)

#     if request.method == "POST":
#         return post_form(
#             request, Purchase, PurchaseForm, purchase_id, next_page="orders:purchases",
#         )

#     return HttpResponse(status=405)


@login_required
@permission_required("orders.delete_purchase", raise_exception=True)
def delete_purchase(request, purchase_id=None):
    purchase_object = get_object_or_404(Purchase, id=purchase_id)
    purchase_object.delete()

    return redirect("orders:purchases")
