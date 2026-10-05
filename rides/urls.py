from django.urls import path
from . import views

app_name = 'rides'

urlpatterns = [
    # Customer
    path('', views.book_ride, name='book_ride'),
    path('ride/<int:ride_id>/', views.ride_detail, name='ride_detail'),
    path('ride/<int:ride_id>/cancel/', views.cancel_ride, name='cancel_ride'),
    path('ride/<int:ride_id>/review/', views.submit_review, name='submit_review'),
    path('my-rides/', views.my_rides, name='my_rides'),
    
    # Captain
    path('captain/', views.captain_dashboard, name='captain_dashboard'),
    path('captain/toggle-online/', views.toggle_online, name='toggle_online'),
    path('captain/ride/<int:ride_id>/accept/', views.accept_ride, name='accept_ride'),
    path('captain/ride/<int:ride_id>/status/', views.update_ride_status, name='update_ride_status'),
]