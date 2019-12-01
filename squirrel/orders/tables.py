from django_tables2 import A, Column, TemplateColumn, tables
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
            "unit",
            "product",
            "state",
            "event",
            "team",
            "unit_price",
            "price",
        ]

    amount = Column(attrs={"td": {"align": "center"}})
    unit = Column(accessor=A("product__unit"))
    edit = TemplateColumn(template_name="tables/order_button_column.html")
    price = Column(empty_values=(), verbose_name="Order sum")

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

        if total:
            return f"{total} €"
        else:
            return "No orders yet."
