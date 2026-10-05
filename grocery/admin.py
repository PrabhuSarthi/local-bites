from django.contrib import admin
from .models import GroceryStore, GroceryCategory, GroceryProduct, GroceryOrder, GroceryOrderItem


@admin.register(GroceryStore)
class GroceryStoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'rating', 'is_active', 'is_approved')
    list_filter = ('is_active', 'is_approved')
    search_fields = ('name', 'owner__username')


@admin.register(GroceryCategory)
class GroceryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'display_order')
    list_filter = ('store',)


@admin.register(GroceryProduct)
class GroceryProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'price', 'unit', 'stock', 'is_available')
    list_filter = ('store', 'is_vegetarian', 'is_available')
    search_fields = ('name',)


class GroceryOrderItemInline(admin.TabularInline):
    model = GroceryOrderItem
    extra = 0


@admin.register(GroceryOrder)
class GroceryOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'store', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'store')
    search_fields = ('order_number', 'customer__username')
    inlines = [GroceryOrderItemInline]