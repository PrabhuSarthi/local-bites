from django.db import models
from django.conf import settings
from django.utils import timezone


class Captain(models.Model):
    """Riding Captain - the driver partner"""
    
    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('auto', 'Auto Rickshaw'),
        ('car', 'Car'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='captain'
    )
    
    # Vehicle
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES, default='bike')
    vehicle_number = models.CharField(max_length=20)
    vehicle_model = models.CharField(max_length=100, blank=True, null=True)
    
    # Documents
    license_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Status
    is_online = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    
    # Metrics
    rating = models.FloatField(default=4.8)
    total_rides = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Current location (fake for demo)
    current_lat = models.FloatField(default=12.9716)
    current_lng = models.FloatField(default=77.5946)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_vehicle_type_display()}"
    
    class Meta:
        ordering = ['-rating']


class Ride(models.Model):
    """A ride booking"""
    
    STATUS_CHOICES = [
        ('searching', 'Finding Captain'),
        ('accepted', 'Captain Assigned'),
        ('arriving', 'Captain Arriving'),
        ('started', 'Ride Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('auto', 'Auto'),
        ('car', 'Car'),
    ]
    
    ride_number = models.CharField(max_length=20, unique=True, blank=True)
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rides'
    )
    captain = models.ForeignKey(
        Captain,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rides'
    )
    
    # Locations
    pickup_address = models.TextField()
    drop_address = models.TextField()
    
    # Distance (in km)
    distance_km = models.FloatField(default=0)
    
    # Vehicle
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_CHOICES, default='bike')
    
    # Fare
    estimated_fare = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_fare = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='searching')
    payment_method = models.CharField(max_length=50, default='Cash')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"#{self.ride_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.ride_number:
            import random
            self.ride_number = f"RID{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class RideReview(models.Model):
    """Customer review for a completed ride"""
    
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=5)  # 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.ride.ride_number} - {self.rating}★"