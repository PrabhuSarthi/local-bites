from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Customer URLs
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    
    # Admin Panel URLs
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/rides/', views.admin_rides, name='admin_rides'),
    path('admin-panel/partners/', views.admin_partners, name='admin_partners'),
    
    # Partner URLs
    path('partner/', views.partner_landing_view, name='partner_landing'),
    path('partner/login/', views.partner_login_view, name='partner_login'),
    path('partner/register/', views.partner_register_view, name='partner_register'),
    path('partner/toggle-open/', views.toggle_restaurant_open, name='toggle_open'),
    
    # Partner: Business pages
    path('partner/earnings/', views.partner_earnings, name='partner_earnings'),
    path('partner/reviews/', views.partner_reviews, name='partner_reviews'),
    path('partner/analytics/', views.partner_analytics, name='partner_analytics'),
    path('partner/settings/', views.partner_settings, name='partner_settings'),
]