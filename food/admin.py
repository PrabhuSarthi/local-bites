from django.contrib import admin
from .models import Restaurant, MenuCategory, FoodItem, Order, OrderItem


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'cuisine', 'rating', 'is_active', 'is_approved')
    list_filter = ('cuisine', 'is_active', 'is_approved')
    search_fields = ('name', 'owner__username')


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'display_order')
    list_filter = ('restaurant',)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price', 'is_vegetarian', 'is_available')
    list_filter = ('restaurant', 'is_vegetarian', 'is_available')
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'restaurant', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'restaurant')
    search_fields = ('order_number', 'customer__username')
    inlines = [OrderItemInline]