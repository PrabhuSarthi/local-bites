from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('restaurant', 'Restaurant Owner'),
        ('grocery', 'Grocery Owner'),
        ('driver', 'Driver'),
        ('customer', 'Customer'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_restaurant(self):
        return self.role == 'restaurant'
    
    def is_grocery(self):
        return self.role == 'grocery'
    
    def is_driver(self):
        return self.role == 'driver'
    
    def is_customer(self):
        return self.role == 'customer'
    
    class Meta:
        db_table = 'users'