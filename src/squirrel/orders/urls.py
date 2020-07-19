from django.urls import path
from squirrel.orders import views

app_name = "orders"

urlpatterns = [
    path("orders", views.OrderListView.as_view(), name="orders"),
    path("orders/new", views.order, name="new_order"),
    path("orders/<int:order_id>", views.order, name="edit_order"),
    path("orders/delete/<int:order_id>", views.delete_order, name="delete_order"),
    path("orders/export", views.export_orders_csv, name="export_orders_csv"),
    path("products", views.ProductListView.as_view(), name="products"),
    path("products/new", views.product, name="new_product"),
    path("products/<int:product_id>", views.product, name="edit_product"),
    path(
        "products/delete/<int:product_id>", views.delete_product, name="delete_product"
    ),
    path("vendors", views.VendorListView.as_view(), name="vendors"),
    path("vendors/new", views.vendor, name="new_vendor"),
    path("vendors/<int:vendor_id>", views.vendor, name="edit_vendor"),
    path("vendors/delete/<int:vendor_id>", views.delete_vendor, name="delete_vendor"),
    path("teams", views.TeamListView.as_view(), name="teams"),
    path("teams/new", views.team, name="new_team"),
    path("teams/<int:team_id>", views.team, name="edit_team"),
    path("teams/delete/<int:team_id>", views.delete_team, name="delete_team"),
    path("events", views.EventListView.as_view(), name="events"),
    path("events/new", views.event, name="new_event"),
    path("events/<int:event_id>", views.event, name="edit_event"),
    path("events/delete/<int:event_id>", views.delete_event, name="delete_event"),
    path("purchases", views.PurchaseListView.as_view(), name="purchases"),
    path("purchases/new", views.purchase, name="new_purchase"),
    path("purchases/<int:purchase_id>", views.purchase, name="edit_purchase"),
    path(
        "purchases/delete/<int:purchase_id>",
        views.delete_purchase,
        name="delete_purchase",
    ),
    path("stockpiles", views.stockpiles, name="stockpiles"),
    path("stockpiles/create", views.create_stockpile, name="create_stockpile"),
    path(
        "stockpiles/<int:stockpile_id>", views.change_stockpile, name="change_stockpile"
    ),
    path(
        "stockpiles/delete/<int:stockpile_id>",
        views.delete_stockpile,
        name="delete_stockpile",
    ),
    path("pillages", views.PillageListView.as_view(), name="pillages"),
    path("pillages/new", views.pillage, name="new_pillage"),
    path("pillages/<int:pillage_id>", views.pillage, name="change_pillage"),
    path(
        "pillages/delete/<int:pillage_id>", views.delete_pillage, name="delete_pillage",
    ),
]
