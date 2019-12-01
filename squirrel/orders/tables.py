from django_tables2 import Column, TemplateColumn, tables
from orders.models import Order, Product, Team


class TeamTable(tables.Table):
    class Meta:
        model = Team
        attrs = {"class": "table table-sm"}
        fields = ["name"]

    edit = TemplateColumn(template_name="tables/team_button_column.html")


class OrderTable(tables.Table):
    class Meta:
        model = Order
        attrs = {"class": "table table-sm"}
        fields = [
            "amount",
            "item",
            "state",
            "event",
            "team",
            "unit_price",
            "price",
        ]

    # The item that is displayed to the user can either be the wish or the configured product
    item = Column(empty_values=())
    edit = TemplateColumn(template_name="tables/order_button_column.html")
    price = Column(empty_values=(), verbose_name="Order sum")

    @staticmethod
    def render_amount(record):

        # A product always has a unit
        if record.product:
            return f"{record.amount} {record.product.unit}"
        else:
            return record.amount

    @staticmethod
    def render_item(record):
        if record.product:
            return record.product
        else:
            return record.wish

    @staticmethod
    def render_price(record):
        if record.amount and record.unit_price:
            order_sum = record.amount * record.unit_price

            return f"{order_sum} €"
        return "—"

    @staticmethod
    def render_unit_price(value):
        return f"{value} €"


class ProductTable(tables.Table):
    class Meta:
        model = Product
        attrs = {"class": "table table-sm"}
        fields = ["name", "unit", "unit_price", "url"]

    edit = TemplateColumn(template_name="tables/product_button_column.html")

    @staticmethod
    def render_unit_price(value):
        return f"{value} €"


class BudgetTable(tables.Table):
    class Meta:
        model = Team
        attrs = {"class": "table table-sm"}
        fields = ["name", "orders_sum"]

    orders_sum = Column(empty_values=(), verbose_name="Orders sum")

    @staticmethod
    def render_orders_sum(record):
        orders = Order.objects.filter(team=record)
        total = sum(order.unit_price * order.amount for order in orders)

        return f"{total} €"
