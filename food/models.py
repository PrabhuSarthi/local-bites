from django.db import models
from django.conf import settings
from django.utils import timezone


class Restaurant(models.Model):
    """Restaurant - owned by a Restaurant Partner"""
    
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='restaurant'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    cuisine = models.CharField(max_length=100, default='Multi-cuisine')
    
    # Timings
    opening_time = models.TimeField(default='09:00')
    closing_time = models.TimeField(default='22:00')
    
    # Metrics (fake for now)
    rating = models.FloatField(default=4.5)
    total_reviews = models.IntegerField(default=0)
    delivery_time = models.IntegerField(default=30, help_text='in minutes')
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    min_order = models.DecimalField(max_digits=6, decimal_places=2, default=100)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    is_open = models.BooleanField(default=True, help_text='Manual open/closed toggle')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def is_currently_open(self):
        """Check if open right now based on hours + manual toggle"""
        if not self.is_open:
            return False
        now = timezone.localtime().time()
        return self.opening_time <= now <= self.closing_time
    
    def get_open_status_text(self):
        """Return display text for customers"""
        now = timezone.localtime()
        
        if not self.is_open:
            return "Currently Closed"
        
        if now.time() < self.opening_time:
            return f"Opens at {self.opening_time.strftime('%I:%M %p')}"
        
        if now.time() > self.closing_time:
            return f"Opens tomorrow at {self.opening_time.strftime('%I:%M %p')}"
        
        return "Open Now"
    
    def get_status_color(self):
        """Return status color for UI"""
        if not self.is_currently_open():
            return 'closed'
        return 'open'
    
    class Meta:
        ordering = ['-rating']


class MenuCategory(models.Model):
    """Categories within a restaurant menu"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    display_order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"
    
    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Menu Categories'


class FoodItem(models.Model):
    """A dish on the menu"""
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Info
    is_vegetarian = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.IntegerField(default=15, help_text='in minutes')
    
    # Metrics
    rating = models.FloatField(default=4.5)
    times_ordered = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
    class Meta:
        ordering = ['name']


class Order(models.Model):
    """A food order"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='food_orders'
    )
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    
    # Address
    delivery_address = models.TextField()
    phone = models.CharField(max_length=15)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=40)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='COD')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"#{self.order_number} - {self.restaurant.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"ORD{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        self.subtotal = sum(item.price * item.quantity for item in self.items.all())
        self.tax = round(float(self.subtotal) * 0.05, 2)
        self.total = float(self.subtotal) + float(self.delivery_fee) + float(self.tax)
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Individual item in an order"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.food_item.name}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity