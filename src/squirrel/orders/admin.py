from django.contrib import admin
from squirrel.orders.models import (
    CostItem,
    Event,
    Order,
    Pillage,
    Product,
    Purchase,
    Stockpile,
    Team,
)

admin.site.register(Event)
admin.site.register(Team)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(Purchase)
admin.site.register(Pillage)
admin.site.register(Stockpile)
admin.site.register(CostItem)
