from django.db import models
from django.conf import settings


class GroceryStore(models.Model):
    """Grocery Store - owned by a Grocery Partner"""
    
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grocery_store'
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='grocery/', blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    
    # Metrics
    rating = models.FloatField(default=4.5)
    total_reviews = models.IntegerField(default=0)
    delivery_time = models.IntegerField(default=15, help_text='in minutes')
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=20)
    min_order = models.DecimalField(max_digits=6, decimal_places=2, default=50)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-rating']


class GroceryCategory(models.Model):
    """Categories within a store (Vegetables, Fruits, Dairy, etc.)"""
    
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    display_order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.store.name} - {self.name}"
    
    class Meta:
        ordering = ['display_order']
        verbose_name_plural = 'Grocery Categories'


class GroceryProduct(models.Model):
    """A product in a grocery store"""
    
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('g', 'Gram'),
        ('ltr', 'Liter'),
        ('ml', 'Milliliter'),
        ('pcs', 'Pieces'),
        ('pack', 'Pack'),
        ('dozen', 'Dozen'),
    ]
    
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(GroceryCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='grocery_products/', blank=True, null=True)
    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')
    
    # Info
    is_vegetarian = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    stock = models.IntegerField(default=100, help_text='Available quantity')
    
    # Metrics
    times_ordered = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.store.name}"
    
    @property
    def is_low_stock(self):
        return self.stock < 10
    
    class Meta:
        ordering = ['name']


class GroceryOrder(models.Model):
    """A grocery order"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('packing', 'Packing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='grocery_orders'
    )
    store = models.ForeignKey(GroceryStore, on_delete=models.CASCADE, related_name='orders')
    
    # Delivery
    delivery_address = models.TextField()
    phone = models.CharField(max_length=15)
    delivery_slot = models.CharField(max_length=50, blank=True, null=True)
    special_instructions = models.TextField(blank=True, null=True)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2, default=20)
    tax = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='COD')
    
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"#{self.order_number} - {self.store.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"GRC{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class GroceryOrderItem(models.Model):
    """Individual item in a grocery order"""
    
    order = models.ForeignKey(GroceryOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(GroceryProduct, on_delete=models.CASCADE)
    
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def subtotal(self):
        return self.price * self.quantity