from django.db.models import Q
from django_tables2 import Column, TemplateColumn, tables
from squirrel.orders.models import Order, Product, Team, Vendor


class VendorTable(tables.Table):
    class Meta:
        model = Vendor
        attrs = {"class": "table table-sm"}
        fields = ["name"]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_vendor %}
        <a class="btn btn-primary btn-sm" href="{% url 'edit_vendor' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_vendor %}
        <a class="btn btn-danger btn-sm" href="{% url 'delete_vendor' record.id %}">Delete</a>
        {% endif %}
    """
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_vendor") or request.user.has_perm(
            "orders.delete_vendor"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")


class TeamTable(tables.Table):
    class Meta:
        model = Team
        attrs = {"class": "table table-sm"}
        fields = ["name"]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_team %}
        <a class="btn btn-primary btn-sm" href="{% url 'edit_team' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_team %}
        <a class="btn btn-danger btn-sm" href="{% url 'delete_team' record.id %}">Delete</a>
        {% endif %}
    """
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_team") or request.user.has_perm(
            "orders.delete_team"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")


class OrderTable(tables.Table):
    class Meta:
        model = Order
        attrs = {"class": "table table-sm"}
        fields = [
            "amount",
            "product",
            "comment",
            "state",
            "event",
            "team",
        ]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_order %}
        <a class="btn btn-primary btn-sm" href="{% url 'edit_order' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_order %}
        <a class="btn btn-danger btn-sm" href="{% url 'delete_order' record.id %}">Delete</a>
        {% endif %}
    """
    )

    comment = TemplateColumn(
        '<data-toggle="tooltip" title="{{record.comment}}">{{record.comment|truncatechars:50}}'
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_order") or request.user.has_perm(
            "orders.delete_order"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")

    @staticmethod
    def render_amount(record):
        return f"{record.amount} {record.product.unit}"


class ProductTable(tables.Table):
    class Meta:
        model = Product
        attrs = {"class": "table table-sm"}
        fields = ["name", "unit", "ordered_amount"]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_product %}
        <a class="btn btn-primary btn-sm" href="{% url 'edit_product' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_product %}
        <a class="btn btn-danger btn-sm" href="{% url 'delete_product' record.id %}">Delete</a>
        {% endif %}
    """
    )

    ordered_amount = Column(
        empty_values=(), verbose_name="Ordered amount not yet on site"
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_product") or request.user.has_perm(
            "orders.delete_product"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")

    @staticmethod
    def render_ordered_amount(record):
        """We get all orders for our product that are NOT ready to pick up AND NOT completed"""
        orders = Order.objects.filter(
            Q(product=record), ~Q(state="REA"), ~Q(state="COM"),
        )

        return sum(order.amount for order in orders)
