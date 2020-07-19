from django_tables2 import TemplateColumn, tables
from squirrel.orders.models import (
    Event,
    Order,
    Pillage,
    Product,
    Purchase,
    Team,
    Vendor,
)


class VendorTable(tables.Table):
    class Meta:
        model = Vendor
        attrs = {"class": "table table-sm"}
        fields = ["name"]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_vendor %}
        <a class="btn btn-primary btn-sm" href="{% url 'orders:edit_vendor' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_vendor %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_vendor' record.id %}">Delete</a>
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
        <a class="btn btn-primary btn-sm" href="{% url 'orders:edit_team' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_team %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_team' record.id %}">Delete</a>
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
        <a class="btn btn-primary btn-sm" href="{% url 'orders:change_order' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_order %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_order' record.id %}">Delete</a>
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
        unit = f"{record.product.unit} " if record.product.unit else ""
        return f"{record.amount} {unit}"


class ProductTable(tables.Table):
    class Meta:
        model = Product
        attrs = {"class": "table table-sm"}
        fields = ["name", "unit", "default_price"]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_product %}
        <a class="btn btn-primary btn-sm" href="{% url 'orders:edit_product' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_product %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_product' record.id %}">Delete</a>
        {% endif %}
    """
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_product") or request.user.has_perm(
            "orders.delete_product"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")


class EventTable(tables.Table):
    class Meta:
        model = Event
        attrs = {"class": "table table-sm"}
        fields = ["name"]

    edit = TemplateColumn(
        """
        {% if perms.orders.change_event %}
        <a class="btn btn-primary btn-sm" href="{% url 'orders:edit_event' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_event %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_event' record.id %}">Delete</a>
        {% endif %}
    """
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_event") or request.user.has_perm(
            "orders.delete_event"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")


class PurchaseTable(tables.Table):
    class Meta:
        model = Purchase
        attrs = {"class": "table table-sm"}

    edit = TemplateColumn(
        """
        {% if perms.orders.change_purchase %}
        <a class="btn btn-primary btn-sm" href="{% url 'orders:change_purchase' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_purchase %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_purchase' record.id %}">Delete</a>
        {% endif %}
    """
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_purchase") or request.user.has_perm(
            "orders.delete_purchase"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")


class PillageTable(tables.Table):
    class Meta:
        model = Pillage
        attrs = {"class": "table table-sm"}

    edit = TemplateColumn(
        """
        {% if perms.orders.change_pillage %}
        <a class="btn btn-primary btn-sm" href="{% url 'orders:change_pillage' record.id %}">Edit</a>
        {% endif %}
        {% if perms.orders.delete_pillage %}
        <a class="btn btn-danger btn-sm" href="{% url 'orders:delete_pillage' record.id %}">Delete</a>
        {% endif %}
    """
    )

    def before_render(self, request):
        if request.user.has_perm("orders.change_pillage") or request.user.has_perm(
            "orders.delete_pillage"
        ):
            self.columns.show("edit")
        else:
            self.columns.hide("edit")
