from django.contrib import admin
from .models import Captain, Ride, RideReview


@admin.register(Captain)
class CaptainAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'vehicle_number', 'is_online', 'rating', 'total_rides')
    list_filter = ('vehicle_type', 'is_online', 'is_approved')
    search_fields = ('user__username', 'vehicle_number')


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('ride_number', 'customer', 'captain', 'vehicle_type', 'status', 'estimated_fare', 'created_at')
    list_filter = ('status', 'vehicle_type', 'created_at')
    search_fields = ('ride_number', 'customer__username')


@admin.register(RideReview)
class RideReviewAdmin(admin.ModelAdmin):
    list_display = ('ride', 'customer', 'rating', 'created_at')
    list_filter = ('rating',)