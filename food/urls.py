from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    # Public
    path('', views.restaurant_list, name='restaurant_list'),
    path('restaurant/<int:restaurant_id>/', views.restaurant_detail, name='restaurant_detail'),
    
    # AJAX Cart APIs
    path('api/cart/add/<int:item_id>/', views.api_add_to_cart, name='api_add_to_cart'),
    path('api/cart/decrease/<int:item_id>/', views.api_decrease_cart, name='api_decrease_cart'),
    path('api/cart/remove/<int:item_id>/', views.api_remove_from_cart, name='api_remove_from_cart'),
    
    # Menu Management
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),
    path('menu/category/add/', views.add_menu_category, name='add_menu_category'),
    path('menu/<int:item_id>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/<int:item_id>/delete/', views.delete_menu_item, name='delete_menu_item'),
    path('menu/<int:item_id>/toggle/', views.api_toggle_item_availability, name='toggle_item_availability'),
    
    # Legacy Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    
    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
    
    # Orders
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/confirmed/', views.order_confirmation, name='order_confirmation'),
    
    # Restaurant Owner
    path('restaurant-orders/', views.restaurant_orders, name='restaurant_orders'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
]