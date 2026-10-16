from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import (
    MenuItem,
    Order,
    OrderItem,
    RestaurantTable,
    Reservation,
    InventoryItem,
    MenuIngredient,
)

admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(RestaurantTable)
admin.site.register(Reservation)
admin.site.register(InventoryItem)
admin.site.register(MenuIngredient)
