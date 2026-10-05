from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Captain, Ride, RideReview


# ==================== FARE CALCULATION ====================

def calculate_fare(vehicle_type, distance_km):
    """Calculate fare based on vehicle type and distance"""
    fares = {
        'bike': {'base': 20, 'per_km': 8},
        'auto': {'base': 30, 'per_km': 12},
        'car': {'base': 50, 'per_km': 18},
    }
    fare_config = fares.get(vehicle_type, fares['bike'])
    return fare_config['base'] + (fare_config['per_km'] * distance_km)


def estimate_distance(pickup, drop):
    """Fake distance estimation"""
    import random
    return round(random.uniform(2, 15), 1)


# ==================== CUSTOMER VIEWS ====================

@login_required
def book_ride(request):
    """Book a ride - main page"""
    if request.method == 'POST':
        pickup = request.POST.get('pickup')
        drop = request.POST.get('drop')
        vehicle_type = request.POST.get('vehicle_type', 'bike')
        
        if not pickup or not drop:
            messages.error(request, 'Please enter pickup and drop locations')
            return redirect('rides:book_ride')
        
        distance = estimate_distance(pickup, drop)
        fare = calculate_fare(vehicle_type, distance)
        
        ride = Ride.objects.create(
            customer=request.user,
            pickup_address=pickup,
            drop_address=drop,
            vehicle_type=vehicle_type,
            distance_km=distance,
            estimated_fare=fare,
            status='searching',
        )
        
        # 🔔 NOTIFY ALL ONLINE CAPTAINS
        from notifications.models import Notification
        online_captains = Captain.objects.filter(
            vehicle_type=vehicle_type,
            is_online=True,
            is_approved=True,
        )
        for captain in online_captains:
            Notification.objects.create(
                user=captain.user,
                title='🏍️ New Ride Request',
                message=f'{ride.get_vehicle_type_display()} ride · {ride.pickup_address[:30]} → {ride.drop_address[:30]} · ₹{ride.estimated_fare}',
                notification_type='ride',
                link=f'/rides/captain/',
                icon='🏍️',
            )
        
        messages.success(request, 'Ride booked! Finding a captain...')
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    preview_distance = 5
    
    context = {
        'bike_fare': calculate_fare('bike', preview_distance),
        'auto_fare': calculate_fare('auto', preview_distance),
        'car_fare': calculate_fare('car', preview_distance),
    }
    return render(request, 'rides/book_ride.html', context)


@login_required
def ride_detail(request, ride_id):
    """Ride tracking page"""
    ride = get_object_or_404(Ride, id=ride_id, customer=request.user)
    
    if ride.status == 'searching':
        available_captain = Captain.objects.filter(
            vehicle_type=ride.vehicle_type,
            is_online=True,
            is_approved=True
        ).first()
        
        if available_captain:
            ride.captain = available_captain
            ride.status = 'accepted'
            ride.accepted_at = timezone.now()
            ride.save()
    
    context = {'ride': ride}
    return render(request, 'rides/ride_detail.html', context)


@login_required
def cancel_ride(request, ride_id):
    """Cancel a ride"""
    ride = get_object_or_404(Ride, id=ride_id, customer=request.user)
    
    if ride.status in ['searching', 'accepted', 'arriving']:
        ride.status = 'cancelled'
        ride.save()
        messages.warning(request, 'Ride cancelled')
    
    return redirect('rides:my_rides')


@login_required
def my_rides(request):
    """Customer's ride history"""
    rides = Ride.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'rides/my_rides.html', {'rides': rides})


@login_required
def submit_review(request, ride_id):
    """Submit a review for a ride"""
    ride = get_object_or_404(Ride, id=ride_id, customer=request.user)
    
    if ride.status != 'completed':
        messages.error(request, 'You can only review completed rides')
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '')
        
        RideReview.objects.create(
            ride=ride,
            customer=request.user,
            rating=rating,
            comment=comment,
        )
        
        if ride.captain:
            captain = ride.captain
            reviews = RideReview.objects.filter(ride__captain=captain)
            if reviews.exists():
                avg_rating = sum(r.rating for r in reviews) / reviews.count()
                captain.rating = round(avg_rating, 1)
                captain.total_rides += 1
                captain.save()
        
        messages.success(request, 'Thanks for your review!')
        return redirect('rides:ride_detail', ride_id=ride.id)
    
    return redirect('rides:ride_detail', ride_id=ride.id)


# ==================== CAPTAIN VIEWS ====================

@login_required
def captain_dashboard(request):
    """Captain's main dashboard"""
    if not request.user.is_driver():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    try:
        captain = request.user.captain
    except Captain.DoesNotExist:
        captain = Captain.objects.create(
            user=request.user,
            vehicle_type='bike',
            vehicle_number='KA-00-XX-0000',
            is_online=False,
        )
        messages.info(request, 'Captain profile created. Please update your vehicle details.')
    
    active_rides = Ride.objects.filter(
        captain=captain,
        status__in=['accepted', 'arriving', 'started']
    ).order_by('-created_at')
    
    pending_rides = Ride.objects.filter(
        status='searching',
        vehicle_type=captain.vehicle_type,
    ).order_by('-created_at')
    
    completed_rides = Ride.objects.filter(
        captain=captain,
        status='completed'
    ).order_by('-completed_at')[:10]
    
    context = {
        'captain': captain,
        'active_rides': active_rides,
        'pending_rides': pending_rides,
        'completed_rides': completed_rides,
    }
    return render(request, 'rides/captain_dashboard.html', context)


@login_required
def toggle_online(request):
    """Toggle captain online/offline status"""
    if not request.user.is_driver():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    try:
        captain = request.user.captain
        captain.is_online = not captain.is_online
        captain.save()
        
        status = 'Online' if captain.is_online else 'Offline'
        messages.success(request, f'You are now {status}')
    except Captain.DoesNotExist:
        messages.error(request, 'Captain profile not found')
    
    return redirect('rides:captain_dashboard')


@login_required
def accept_ride(request, ride_id):
    """Captain accepts a ride"""
    if not request.user.is_driver():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    ride = get_object_or_404(Ride, id=ride_id, status='searching')
    
    try:
        captain = request.user.captain
        ride.captain = captain
        ride.status = 'accepted'
        ride.accepted_at = timezone.now()
        ride.save()
        
        # 🔔 NOTIFY CUSTOMER
        from notifications.models import Notification
        captain_name = captain.user.get_full_name or captain.user.username
        Notification.objects.create(
            user=ride.customer,
            title='✅ Captain Assigned!',
            message=f'{captain_name} ({captain.vehicle_number}) accepted your ride',
            notification_type='ride',
            link=f'/rides/ride/{ride.id}/',
            icon='✅',
        )
        
        messages.success(request, f'Ride #{ride.ride_number} accepted!')
    except Captain.DoesNotExist:
        messages.error(request, 'Captain profile not found')
    
    return redirect('rides:captain_dashboard')


@login_required
def update_ride_status(request, ride_id):
    """Captain updates ride status"""
    if not request.user.is_driver():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    ride = get_object_or_404(Ride, id=ride_id)
    
    if ride.captain != request.user.captain:
        messages.error(request, 'Access denied')
        return redirect('rides:captain_dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in dict(Ride.STATUS_CHOICES):
            ride.status = new_status
            
            if new_status == 'started':
                ride.started_at = timezone.now()
            elif new_status == 'completed':
                ride.completed_at = timezone.now()
                ride.final_fare = ride.estimated_fare
                captain = ride.captain
                captain.total_earnings += ride.final_fare
                captain.save()
            
            ride.save()
            
            # 🔔 NOTIFY CUSTOMER
            from notifications.models import Notification
            status_icons = {
                'started': '🏍️',
                'completed': '🎉',
                'cancelled': '❌',
            }
            if new_status in status_icons:
                Notification.objects.create(
                    user=ride.customer,
                    title=f'{status_icons[new_status]} Ride {ride.get_status_display()}',
                    message=f'Your ride #{ride.ride_number} is now {ride.get_status_display().lower()}',
                    notification_type='ride',
                    link=f'/rides/ride/{ride.id}/',
                    icon=status_icons[new_status],
                )
            
            messages.success(request, f'Ride status updated to {ride.get_status_display()}')
    
    return redirect('rides:captain_dashboard')