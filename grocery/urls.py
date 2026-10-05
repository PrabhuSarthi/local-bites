from django.urls import path
from . import views

app_name = 'grocery'

urlpatterns = [
    # Public
    path('', views.store_list, name='store_list'),
    path('store/<int:store_id>/', views.store_detail, name='store_detail'),
    
    # AJAX Cart APIs
    path('api/cart/add/<int:product_id>/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/decrease/<int:product_id>/', views.api_decrease_cart, name='api_decrease_cart'),
    path('api/cart/remove/<int:product_id>/', views.api_remove_from_cart, name='api_remove_from_cart'),
    
    # Legacy Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    
    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    
    # Orders
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/confirmed/', views.order_confirmation, name='order_confirmation'),
    
    # Owner
    path('store-orders/', views.store_orders, name='store_orders'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
]