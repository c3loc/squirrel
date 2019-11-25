from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django_tables2 import SingleTableView
from .models import Order, Team, Event, Product
from .tables import OrderTable, ProductTable
from .forms import OrderForm, ProductForm


def login_redirect(request):
    return redirect('login')


def overview(request):
    return render(request, 'overview.html')


class OrderListView(LoginRequiredMixin, SingleTableView):
    model = Order
    table_class = OrderTable
    template_name = 'orders.html'


class ProductListView(LoginRequiredMixin, SingleTableView):
    model = Product
    table_class = ProductTable
    template_name = 'products.html'


@login_required
def order(request, order_id=None):
    user = User.objects.first()  # TODO: get the currently logged in user

    if order_id:
        order_object = Order.objects.get(id=order_id)
    else:
        order_object = None

    if request.method == 'POST':
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

            return redirect('orders')
    else:
        if order_object:
            form = OrderForm(instance=order_object)
        else:
            form = OrderForm()

    return render(request, 'order.html', {'form': form, 'teams': Team.objects.all(), 'events': Event.objects.all()})


@login_required
def delete_order(request, order_id=None):
    # TODO: Check that user has rights to delete order
    order_object = get_object_or_404(Order, id=order_id)
    order_object.delete()

    return redirect('orders')


@login_required
def product(request, product_id=None):
    user = User.objects.first()  # TODO: get the currently logged in user

    if product_id:
        product_object = Product.objects.get(id=product_id)
    else:
        product_object = None

    if request.method == 'POST':
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

            return redirect('orders')
    else:
        if product_object:
            form = ProductForm(instance=product_object)
        else:
            form = ProductForm()

    return render(request, 'product.html', {'form': form})


@login_required
def delete_product(request, product_id=None):
    # TODO: Check that user has rights to delete product
    product_object = get_object_or_404(Product, id=product_id)
    product_object.delete()

    return redirect('products')
