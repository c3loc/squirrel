from django_tables2 import A, Column, TemplateColumn, tables
from orders.models import Order, Product


class OrderTable(tables.Table):
    class Meta:
        model = Order
        attrs = {"class": "table table-sm"}
        fields = ["amount", "unit", "product", "state", "event", "team"]

    amount = Column(attrs={"td": {"align": "center"}})
    unit = Column(accessor=A("product__unit"))
    edit = TemplateColumn(template_name="tables/order_button_column.html")


class ProductTable(tables.Table):
    class Meta:
        model = Product
        attrs = {"class": "table table-sm"}
        fields = ["name", "unit", "unit_price", "url"]

    edit = TemplateColumn(template_name="tables/product_button_column.html")
