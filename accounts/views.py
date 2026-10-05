from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import CustomUser
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def home_view(request):
    """Landing page"""
    return render(request, 'index.html')


def register_view(request):
    """User registration - customer only"""
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'customer'
            user.save()
            login(request, user)
            return redirect('/dashboard/')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Customer login - silent success, only errors shown"""
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.role in ['restaurant', 'grocery', 'driver']:
                error = 'This is the customer portal. Partners should login at the Partner Portal.'
            else:
                login(request, user)
                return redirect('/dashboard/')
        else:
            error = 'Invalid username or password'
    
    return render(request, 'accounts/login.html', {'error': error})


def logout_view(request):
    """User logout - redirect based on role, silent"""
    user_role = None
    if request.user.is_authenticated:
        user_role = request.user.role
    
    logout(request)
    
    if user_role in ['restaurant', 'grocery', 'driver']:
        return redirect('/partner/login/')
    else:
        return redirect('/')


@login_required
def dashboard_view(request):
    """Role-based dashboard"""
    user = request.user
    
    if user.is_admin():
        return redirect('/admin-panel/')
    
    elif user.is_restaurant():
        from food.models import Restaurant, Order as FoodOrder
        from notifications.models import Notification
        from django.utils import timezone
        
        try:
            restaurant = user.restaurant
        except Restaurant.DoesNotExist:
            restaurant = None
        
        recent_orders = []
        today_revenue = 0
        orders_today = 0
        avg_order_value = 0
        pending_count = 0
        
        if restaurant:
            orders = FoodOrder.objects.filter(restaurant=restaurant)
            recent_orders = orders.order_by('-created_at')[:5]
            
            today = timezone.now().date()
            today_orders = orders.filter(created_at__date=today)
            orders_today = today_orders.count()
            
            delivered = orders.filter(status='delivered')
            if delivered.exists():
                total_rev = sum(o.total for o in delivered)
                today_revenue = round(total_rev, 2)
                avg_order_value = round(total_rev / delivered.count(), 2)
            
            pending_count = orders.filter(status='pending').count()
        
        unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
        
        return render(request, 'partner/dashboard_restaurant.html', {
            'user': user,
            'restaurant': restaurant,
            'recent_orders': recent_orders,
            'today_revenue': today_revenue,
            'orders_today': orders_today,
            'avg_order_value': avg_order_value,
            'pending_count': pending_count,
            'unread_notifications': unread_notifications,
        })
    
    elif user.is_grocery():
        from grocery.models import GroceryStore, GroceryOrder
        from notifications.models import Notification
        from django.utils import timezone
        
        try:
            store = user.grocery_store
        except GroceryStore.DoesNotExist:
            store = None
        
        recent_orders = []
        today_revenue = 0
        orders_today = 0
        low_stock_count = 0
        pending_count = 0
        
        if store:
            orders = GroceryOrder.objects.filter(store=store)
            recent_orders = orders.order_by('-created_at')[:5]
            
            today = timezone.now().date()
            orders_today = orders.filter(created_at__date=today).count()
            
            delivered = orders.filter(status='delivered')
            if delivered.exists():
                today_revenue = round(sum(o.total for o in delivered), 2)
            
            low_stock_count = store.products.filter(stock__lt=10).count()
            pending_count = orders.filter(status='pending').count()
        
        unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
        
        return render(request, 'partner/dashboard_grocery.html', {
            'user': user,
            'store': store,
            'recent_orders': recent_orders,
            'today_revenue': today_revenue,
            'orders_today': orders_today,
            'low_stock_count': low_stock_count,
            'pending_count': pending_count,
            'unread_notifications': unread_notifications,
        })
    
    elif user.is_driver():
        return redirect('/rides/captain/')
    
    elif user.is_customer():
        return render(request, 'accounts/dashboard_customer.html', {'user': user})
    
    else:
        return render(request, 'accounts/dashboard.html', {'user': user})


@login_required
def toggle_restaurant_open(request):
    """Toggle restaurant open/closed status"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('/dashboard/')
    
    try:
        restaurant = request.user.restaurant
        restaurant.is_open = not restaurant.is_open
        restaurant.save()
        status = 'Open' if restaurant.is_open else 'Closed'
        messages.success(request, f'Restaurant is now {status}')
    except Exception:
        pass
    
    return redirect('/dashboard/')


@login_required
def profile_view(request):
    """View own profile - role-aware with stats"""
    user = request.user
    context = {'user': user}
    
    is_customer = user.is_customer()
    
    if user.is_customer():
        from food.models import Order as FoodOrder
        from grocery.models import GroceryOrder
        from rides.models import Ride
        
        food_orders = FoodOrder.objects.filter(customer=user)
        grocery_orders = GroceryOrder.objects.filter(customer=user)
        rides = Ride.objects.filter(customer=user)
        
        total_spent = (
            sum(o.total for o in food_orders) +
            sum(o.total for o in grocery_orders) +
            sum(r.final_fare or r.estimated_fare for r in rides if r.status == 'completed')
        )
        
        context.update({
            'total_food_orders': food_orders.count(),
            'total_grocery_orders': grocery_orders.count(),
            'total_rides': rides.count(),
            'total_spent': total_spent,
            'recent_food_orders': food_orders.order_by('-created_at')[:3],
            'recent_grocery_orders': grocery_orders.order_by('-created_at')[:3],
            'recent_rides': rides.order_by('-created_at')[:3],
        })
    
    elif user.is_restaurant():
        from food.models import Restaurant, Order as FoodOrder
        try:
            restaurant = user.restaurant
            orders = FoodOrder.objects.filter(restaurant=restaurant)
            total_revenue = sum(o.total for o in orders if o.status == 'delivered')
            context.update({
                'restaurant': restaurant,
                'total_orders': orders.count(),
                'pending_orders': orders.filter(status='pending').count(),
                'total_revenue': total_revenue,
                'total_items': restaurant.items.count(),
                'recent_orders': orders.order_by('-created_at')[:5],
            })
        except Restaurant.DoesNotExist:
            context['restaurant'] = None
    
    elif user.is_grocery():
        from grocery.models import GroceryStore, GroceryOrder
        try:
            store = user.grocery_store
            orders = GroceryOrder.objects.filter(store=store)
            total_revenue = sum(o.total for o in orders if o.status == 'delivered')
            context.update({
                'store': store,
                'total_orders': orders.count(),
                'pending_orders': orders.filter(status='pending').count(),
                'total_revenue': total_revenue,
                'total_products': store.products.count(),
                'low_stock_count': store.products.filter(stock__lt=10).count(),
                'recent_orders': orders.order_by('-created_at')[:5],
            })
        except GroceryStore.DoesNotExist:
            context['store'] = None
    
    elif user.is_driver():
        from rides.models import Captain, Ride
        try:
            captain = user.captain
            rides = Ride.objects.filter(captain=captain)
            completed_rides = rides.filter(status='completed')
            context.update({
                'captain': captain,
                'total_rides': rides.count(),
                'completed_rides': completed_rides.count(),
                'total_earnings': captain.total_earnings,
                'recent_rides': rides.order_by('-created_at')[:5],
            })
        except Captain.DoesNotExist:
            context['captain'] = None
    
    elif user.is_admin():
        from food.models import Order as FoodOrder
        from grocery.models import GroceryOrder
        from rides.models import Ride
        context.update({
            'total_users': CustomUser.objects.count(),
            'total_food_orders': FoodOrder.objects.count(),
            'total_grocery_orders': GroceryOrder.objects.count(),
            'total_rides': Ride.objects.count(),
        })
    
    if is_customer:
        return render(request, 'accounts/profile_customer.html', context)
    else:
        return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit own profile - role-aware template"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('/profile/')
    else:
        form = UserProfileForm(instance=request.user)
    
    if request.user.is_customer():
        return render(request, 'accounts/edit_profile_customer.html', {'form': form})
    else:
        return render(request, 'accounts/edit_profile.html', {'form': form})


# ==================== ADMIN PANEL VIEWS ====================

@login_required
def admin_dashboard(request):
    if not request.user.is_admin():
        return redirect('/dashboard/')
    
    from food.models import Restaurant, Order as FoodOrder
    from grocery.models import GroceryStore, GroceryOrder
    from rides.models import Captain, Ride
    
    context = {
        'total_customers': CustomUser.objects.filter(role='customer').count(),
        'total_restaurant_owners': CustomUser.objects.filter(role='restaurant').count(),
        'total_grocery_owners': CustomUser.objects.filter(role='grocery').count(),
        'total_captains': CustomUser.objects.filter(role='driver').count(),
        'total_restaurants': Restaurant.objects.count(),
        'total_grocery_stores': GroceryStore.objects.count(),
        'total_riders': Captain.objects.count(),
        'food_orders': FoodOrder.objects.count(),
        'grocery_orders': GroceryOrder.objects.count(),
        'total_rides': Ride.objects.count(),
        'recent_users': CustomUser.objects.order_by('-date_joined')[:8],
        'recent_food_orders': FoodOrder.objects.order_by('-created_at')[:5],
        'recent_grocery_orders': GroceryOrder.objects.order_by('-created_at')[:5],
        'recent_rides': Ride.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def admin_users(request):
    if not request.user.is_admin():
        return redirect('/dashboard/')
    
    role_filter = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    search = request.GET.get('q', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'role_filter': role_filter,
        'search': search,
        'total_users': CustomUser.objects.count(),
        'customers': CustomUser.objects.filter(role='customer').count(),
        'restaurants': CustomUser.objects.filter(role='restaurant').count(),
        'groceries': CustomUser.objects.filter(role='grocery').count(),
        'drivers': CustomUser.objects.filter(role='driver').count(),
    }
    return render(request, 'admin_panel/users.html', context)


@login_required
def admin_orders(request):
    if not request.user.is_admin():
        return redirect('/dashboard/')
    
    from food.models import Order as FoodOrder
    from grocery.models import GroceryOrder
    
    food_orders = FoodOrder.objects.all().order_by('-created_at')[:50]
    grocery_orders = GroceryOrder.objects.all().order_by('-created_at')[:50]
    
    context = {
        'food_orders': food_orders,
        'grocery_orders': grocery_orders,
        'total_food_orders': FoodOrder.objects.count(),
        'total_grocery_orders': GroceryOrder.objects.count(),
    }
    return render(request, 'admin_panel/orders.html', context)


@login_required
def admin_rides(request):
    if not request.user.is_admin():
        return redirect('/dashboard/')
    
    from rides.models import Ride, Captain
    
    rides = Ride.objects.all().order_by('-created_at')[:50]
    captains = Captain.objects.all().order_by('-rating')
    
    context = {
        'rides': rides,
        'captains': captains,
        'total_rides': Ride.objects.count(),
        'total_captains': Captain.objects.count(),
    }
    return render(request, 'admin_panel/rides.html', context)


@login_required
def admin_partners(request):
    if not request.user.is_admin():
        return redirect('/dashboard/')
    
    from food.models import Restaurant
    from grocery.models import GroceryStore
    from rides.models import Captain
    
    context = {
        'restaurants': Restaurant.objects.all(),
        'grocery_stores': GroceryStore.objects.all(),
        'captains': Captain.objects.all(),
    }
    return render(request, 'admin_panel/partners.html', context)


# ==================== PARTNER VIEWS ====================

def partner_landing_view(request):
    """Partner landing page"""
    return render(request, 'partner/landing.html')


def partner_login_view(request):
    """Partner login - silent success, only errors shown"""
    if request.user.is_authenticated:
        if request.user.role in ['restaurant', 'grocery', 'driver']:
            return redirect('/dashboard/')
        else:
            return redirect('/dashboard/')
    
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.role in ['restaurant', 'grocery', 'driver']:
                login(request, user)
                return redirect('/dashboard/')
            else:
                error = 'This is the partner portal. Please use the customer login instead.'
        else:
            error = 'Invalid username or password'
    
    return render(request, 'partner/login.html', {'error': error})


def partner_register_view(request):
    """Partner registration page"""
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role not in ['restaurant', 'grocery', 'driver']:
                user.role = 'restaurant'
            user.save()
            login(request, user)
            return redirect('/dashboard/')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'partner/register.html', {'form': form})


# ==================== PARTNER: EARNINGS ====================

@login_required
def partner_earnings(request):
    """Earnings page - real data from delivered orders"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('/dashboard/')

    try:
        restaurant = request.user.restaurant
    except Exception:
        messages.error(request, 'No restaurant found.')
        return redirect('/dashboard/')

    from food.models import Order
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    all_delivered = Order.objects.filter(restaurant=restaurant, status='delivered')

    total_revenue = sum(float(o.total) for o in all_delivered)

    today_orders = all_delivered.filter(created_at__date=today)
    today_revenue = sum(float(o.total) for o in today_orders)

    week_orders = all_delivered.filter(created_at__gte=week_ago)
    week_revenue = sum(float(o.total) for o in week_orders)

    month_orders = all_delivered.filter(created_at__gte=month_ago)
    month_revenue = sum(float(o.total) for o in month_orders)

    total_count = all_delivered.count()
    avg_order = round(total_revenue / total_count, 2) if total_count else 0

    recent = all_delivered.order_by('-delivered_at', '-created_at')[:10]

    context = {
        'restaurant': restaurant,
        'total_revenue': round(total_revenue, 2),
        'today_revenue': round(today_revenue, 2),
        'week_revenue': round(week_revenue, 2),
        'month_revenue': round(month_revenue, 2),
        'avg_order': avg_order,
        'total_orders': total_count,
        'recent': recent,
    }
    return render(request, 'partner/earnings.html', context)


# ==================== PARTNER: REVIEWS ====================

@login_required
def partner_reviews(request):
    """Reviews page - restaurant rating + top items"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('/dashboard/')

    try:
        restaurant = request.user.restaurant
    except Exception:
        messages.error(request, 'No restaurant found.')
        return redirect('/dashboard/')

    top_rated = restaurant.items.order_by('-rating')[:8]
    most_ordered = restaurant.items.order_by('-times_ordered')[:8]

    context = {
        'restaurant': restaurant,
        'top_rated': top_rated,
        'most_ordered': most_ordered,
    }
    return render(request, 'partner/reviews.html', context)


# ==================== PARTNER: ANALYTICS ====================

@login_required
def partner_analytics(request):
    """Analytics page - real data from orders"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('/dashboard/')

    try:
        restaurant = request.user.restaurant
    except Exception:
        messages.error(request, 'No restaurant found.')
        return redirect('/dashboard/')

    from food.models import Order
    from django.utils import timezone
    from datetime import timedelta

    orders = Order.objects.filter(restaurant=restaurant)

    status_counts = {}
    for code, label in Order.STATUS_CHOICES:
        status_counts[code] = {
            'label': label,
            'count': orders.filter(status=code).count(),
        }

    now = timezone.now()
    daily = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_orders = orders.filter(status='delivered', created_at__date=day)
        day_rev = sum(float(o.total) for o in day_orders)
        daily.append({
            'date': day.strftime('%a'),
            'revenue': round(day_rev, 2),
            'orders': day_orders.count(),
        })

    max_revenue = max([d['revenue'] for d in daily]) if daily else 1
    if max_revenue == 0:
        max_revenue = 1

    top_items = restaurant.items.order_by('-times_ordered')[:5]

    total_orders = orders.count()
    delivered_orders = orders.filter(status='delivered').count()
    cancelled_orders = orders.filter(status='cancelled').count()

    context = {
        'restaurant': restaurant,
        'status_counts': status_counts,
        'daily': daily,
        'max_revenue': max_revenue,
        'top_items': top_items,
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
    }
    return render(request, 'partner/analytics.html', context)


# ==================== PARTNER: SETTINGS ====================

@login_required
def partner_settings(request):
    """Settings page - edit restaurant details"""
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('/dashboard/')

    try:
        restaurant = request.user.restaurant
    except Exception:
        messages.error(request, 'No restaurant found.')
        return redirect('/dashboard/')

    if request.method == 'POST':
        restaurant.name = request.POST.get('name', restaurant.name)
        restaurant.description = request.POST.get('description', restaurant.description)
        restaurant.cuisine = request.POST.get('cuisine', restaurant.cuisine)
        restaurant.address = request.POST.get('address', restaurant.address)
        restaurant.phone = request.POST.get('phone', restaurant.phone)

        opening = request.POST.get('opening_time')
        closing = request.POST.get('closing_time')
        if opening:
            restaurant.opening_time = opening
        if closing:
            restaurant.closing_time = closing

        try:
            restaurant.delivery_fee = float(request.POST.get('delivery_fee', restaurant.delivery_fee))
        except (TypeError, ValueError):
            pass
        try:
            restaurant.min_order = float(request.POST.get('min_order', restaurant.min_order))
        except (TypeError, ValueError):
            pass
        try:
            restaurant.delivery_time = int(request.POST.get('delivery_time', restaurant.delivery_time))
        except (TypeError, ValueError):
            pass

        restaurant.save()
        messages.success(request, 'Restaurant settings updated!')
        return redirect('/partner/settings/')

    return render(request, 'partner/settings.html', {'restaurant': restaurant})