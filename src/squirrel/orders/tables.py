from django_tables2 import TemplateColumn, tables
from squirrel.orders.models import Event, Product, Team, Vendor


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
