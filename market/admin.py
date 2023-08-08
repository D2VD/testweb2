from django.contrib import admin
from .models import Item, OrderItem, Order
from cities_light.models import City, Country, Region


class ItemAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ("title", "price", "recently")
    # Allow searching by these fields
    search_fields = ("title", "description")
    # Allow filtering by these fields
    list_filter = ("price", "category")
    # Allow editing these fields in the detail view
    fields = (
        "title",
        "price",
        "discount_price",
        "description",
        "category",
        "date",
        "image",
    )


admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order)
