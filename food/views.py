from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Restaurant, MenuCategory, FoodItem, Order, OrderItem


def _build_cart_payload(request):
    """Helper: build full cart data for API responses"""
    cart = request.session.get('food_cart', {})
    restaurant_id = request.session.get('food_cart_restaurant')
    
    items_data = []
    subtotal = 0
    restaurant_name = None
    
    if cart and restaurant_id:
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            restaurant_name = restaurant.name
            for item_id_str, qty in cart.items():
                try:
                    item = FoodItem.objects.get(id=int(item_id_str))
                    item_total = float(item.price) * qty
                    items_data.append({
                        'id': item.id,
                        'name': item.name,
                        'price': float(item.price),
                        'quantity': qty,
                        'subtotal': round(item_total, 2),
                    })
                    subtotal += item_total
                except FoodItem.DoesNotExist:
                    pass
        except Restaurant.DoesNotExist:
            pass
    
    return {
        'items': items_data,
        'subtotal': round(subtotal, 2),
        'restaurant_name': restaurant_name,
        'cart_count': sum(cart.values()) if cart else 0,
    }


def restaurant_list(request):
    """Public restaurant listing"""
    restaurants = Restaurant.objects.filter(is_active=True, is_approved=True)
    
    search = request.GET.get('q', '')
    if search:
        restaurants = restaurants.filter(
            Q(name__icontains=search) |
            Q(cuisine__icontains=search) |
            Q(description__icontains=search)
        )
    
    cuisine = request.GET.get('cuisine', '')
    if cuisine:
        restaurants = restaurants.filter(cuisine__iexact=cuisine)
    
    all_cuisines = Restaurant.objects.filter(
        is_active=True, is_approved=True
    ).values_list('cuisine', flat=True).distinct()
    
    context = {
        'restaurants': restaurants,
        'all_cuisines': all_cuisines,
        'search': search,
        'selected_cuisine': cuisine,
    }
    return render(request, 'food/restaurant_list.html', context)


def restaurant_detail(request, restaurant_id):
    """Restaurant detail + menu"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id, is_active=True)
    categories = restaurant.categories.all().prefetch_related('items')
    
    cart = request.session.get('food_cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    initial_cart = _build_cart_payload(request)
    
    context = {
        'restaurant': restaurant,
        'categories': categories,
        'cart_count': cart_count,
        'cart': cart,
        'initial_cart': initial_cart,
    }
    return render(request, 'food/restaurant_detail.html', context)


# ==================== AJAX CART APIS ====================

def api_add_to_cart(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    cart = request.session.get('food_cart', {})
    cart_restaurant = request.session.get('food_cart_restaurant', None)
    cart_cleared = False
    if cart_restaurant and cart_restaurant != item.restaurant.id:
        cart = {}
        cart_cleared = True
    item_id_str = str(item_id)
    cart[item_id_str] = cart.get(item_id_str, 0) + 1
    request.session['food_cart'] = cart
    request.session['food_cart_restaurant'] = item.restaurant.id
    request.session.modified = True
    payload = _build_cart_payload(request)
    payload.update({'success': True, 'item_id': item.id, 'item_count': cart[item_id_str], 'cart_cleared': cart_cleared})
    return JsonResponse(payload)


def api_decrease_cart(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    cart = request.session.get('food_cart', {})
    item_id_str = str(item_id)
    if item_id_str in cart:
        cart[item_id_str] -= 1
        if cart[item_id_str] <= 0:
            del cart[item_id_str]
    request.session['food_cart'] = cart
    request.session.modified = True
    if not cart:
        request.session.pop('food_cart_restaurant', None)
    payload = _build_cart_payload(request)
    payload.update({'success': True, 'item_id': item.id, 'item_count': cart.get(item_id_str, 0)})
    return JsonResponse(payload)


def api_remove_from_cart(request, item_id):
    item_id_str = str(item_id)
    cart = request.session.get('food_cart', {})
    if item_id_str in cart:
        del cart[item_id_str]
    request.session['food_cart'] = cart
    request.session.modified = True
    if not cart:
        request.session.pop('food_cart_restaurant', None)
    payload = _build_cart_payload(request)
    payload.update({'success': True, 'item_id': int(item_id), 'item_count': 0})
    return JsonResponse(payload)


def add_to_cart(request, item_id):
    item = get_object_or_404(FoodItem, id=item_id)
    cart = request.session.get('food_cart', {})
    cart_restaurant = request.session.get('food_cart_restaurant', None)
    if cart_restaurant and cart_restaurant != item.restaurant.id:
        cart = {}
    item_id_str = str(item_id)
    cart[item_id_str] = cart.get(item_id_str, 0) + 1
    request.session['food_cart'] = cart
    request.session['food_cart_restaurant'] = item.restaurant.id
    request.session.modified = True
    return redirect('food:restaurant_detail', restaurant_id=item.restaurant.id)


def cart_view(request):
    cart = request.session.get('food_cart', {})
    restaurant_id = request.session.get('food_cart_restaurant')
    items = []
    subtotal = 0
    restaurant = None
    if cart and restaurant_id:
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        for item_id_str, qty in cart.items():
            try:
                item = FoodItem.objects.get(id=int(item_id_str))
                item_total = float(item.price) * qty
                items.append({'item': item, 'quantity': qty, 'total': item_total})
                subtotal += item_total
            except FoodItem.DoesNotExist:
                pass
    delivery_fee = float(restaurant.delivery_fee) if restaurant else 0
    tax = round(subtotal * 0.05, 2)
    total = subtotal + delivery_fee + tax
    context = {
        'items': items, 'restaurant': restaurant, 'subtotal': subtotal,
        'delivery_fee': delivery_fee, 'tax': tax, 'total': total,
        'cart_count': sum(cart.values()) if cart else 0,
    }
    return render(request, 'food/cart.html', context)


def update_cart(request, item_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = request.session.get('food_cart', {})
        item_id_str = str(item_id)
        if item_id_str in cart:
            if action == 'increase':
                cart[item_id_str] += 1
            elif action == 'decrease':
                cart[item_id_str] -= 1
                if cart[item_id_str] <= 0:
                    del cart[item_id_str]
            elif action == 'remove':
                del cart[item_id_str]
        request.session['food_cart'] = cart
        request.session.modified = True
        if not cart:
            request.session.pop('food_cart_restaurant', None)
    return redirect('food:cart')


@login_required
def checkout_view(request):
    cart = request.session.get('food_cart', {})
    restaurant_id = request.session.get('food_cart_restaurant')
    if not cart or not restaurant_id:
        messages.warning(request, 'Your cart is empty')
        return redirect('food:restaurant_list')
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    items = []
    subtotal = 0
    for item_id_str, qty in cart.items():
        try:
            item = FoodItem.objects.get(id=int(item_id_str))
            items.append({'item': item, 'quantity': qty, 'total': float(item.price) * qty})
            subtotal += float(item.price) * qty
        except FoodItem.DoesNotExist:
            pass
    delivery_fee = float(restaurant.delivery_fee)
    tax = round(subtotal * 0.05, 2)
    total = subtotal + delivery_fee + tax
    if request.method == 'POST':
        order = Order.objects.create(
            customer=request.user, restaurant=restaurant,
            delivery_address=request.POST.get('address', request.user.address or ''),
            phone=request.POST.get('phone', request.user.phone or ''),
            special_instructions=request.POST.get('instructions', ''),
            subtotal=subtotal, delivery_fee=delivery_fee, tax=tax, total=total,
            payment_method=request.POST.get('payment_method', 'COD'),
        )
        for item_data in items:
            OrderItem.objects.create(order=order, food_item=item_data['item'], quantity=item_data['quantity'], price=item_data['item'].price)
            item_data['item'].times_ordered += item_data['quantity']
            item_data['item'].save()
        from notifications.models import Notification
        customer_name = request.user.get_full_name()
        if not customer_name:
            customer_name = request.user.username
        Notification.objects.create(
            user=restaurant.owner, title='🍽️ New Food Order!',
            message=f'Order #{order.order_number} received from {customer_name} · ₹{order.total}',
            notification_type='order', link=f'/food/restaurant-orders/', icon='🍽️',
        )
        request.session.pop('food_cart', None)
        request.session.pop('food_cart_restaurant', None)
        messages.success(request, f'Order placed! Order #{order.order_number}')
        return redirect('food:order_confirmation', order_id=order.id)
    context = {'items': items, 'restaurant': restaurant, 'subtotal': subtotal, 'delivery_fee': delivery_fee, 'tax': tax, 'total': total}
    return render(request, 'food/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'food/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'food/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.user.is_customer() and order.customer != request.user:
        messages.error(request, 'Access denied')
        return redirect('food:restaurant_list')
    if request.user.is_restaurant() and order.restaurant.owner != request.user:
        messages.error(request, 'Access denied')
        return redirect('food:restaurant_list')
    if request.user.is_restaurant():
        return render(request, 'food/order_detail_restaurant.html', {'order': order})
    return render(request, 'food/order_detail.html', {'order': order})


@login_required
def restaurant_orders(request):
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, 'No restaurant found.')
        return redirect('dashboard')
    orders = Order.objects.filter(restaurant=restaurant).order_by('-created_at')
    return render(request, 'food/restaurant_orders.html', {'restaurant': restaurant, 'orders': orders})


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not request.user.is_restaurant() or order.restaurant.owner != request.user:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'delivered':
                from django.utils import timezone
                order.delivered_at = timezone.now()
            order.save()
            from notifications.models import Notification
            status_icons = {'confirmed': '✅', 'preparing': '👨‍🍳', 'out_for_delivery': '🛵', 'delivered': '🎉', 'cancelled': '❌'}
            Notification.objects.create(
                user=order.customer,
                title=f'{status_icons.get(new_status, "📦")} Order {order.get_status_display()}',
                message=f'Your food order #{order.order_number} from {order.restaurant.name} is now {order.get_status_display().lower()}',
                notification_type='order', link=f'/food/orders/{order.id}/', icon=status_icons.get(new_status, '📦'),
            )
            messages.success(request, f'Order #{order.order_number} status updated')
    referer = request.META.get('HTTP_REFERER', '')
    if f'/food/orders/{order_id}/' in referer:
        return redirect('food:order_detail', order_id=order.id)
    return redirect('food:restaurant_orders')


# ========== MENU MANAGEMENT VIEWS ==========

@login_required
def menu_management(request):
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, 'No restaurant found.')
        return redirect('dashboard')
    categories = restaurant.categories.all().prefetch_related('items')
    return render(request, 'partner/menu_manage.html', {'restaurant': restaurant, 'categories': categories})


@login_required
def add_menu_item(request):
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, 'No restaurant found.')
        return redirect('dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        is_vegetarian = request.POST.get('is_vegetarian') == 'veg'
        is_available = request.POST.get('is_available') == 'on'
        category = None
        if category_id:
            try:
                category = MenuCategory.objects.get(id=category_id, restaurant=restaurant)
            except MenuCategory.DoesNotExist:
                pass
        FoodItem.objects.create(
            restaurant=restaurant, category=category, name=name,
            description=description, price=price,
            is_vegetarian=is_vegetarian, is_available=is_available,
        )
        messages.success(request, f'"{name}" added to menu!')
        return redirect('food:menu_management')
    categories = restaurant.categories.all()
    return render(request, 'partner/add_menu_item.html', {'restaurant': restaurant, 'categories': categories})


@login_required
def edit_menu_item(request, item_id):
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    item = get_object_or_404(FoodItem, id=item_id)
    if item.restaurant.owner != request.user:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description', '')
        item.price = request.POST.get('price')
        category_id = request.POST.get('category')
        item.is_vegetarian = request.POST.get('is_vegetarian') == 'veg'
        item.is_available = request.POST.get('is_available') == 'on'
        if category_id:
            try:
                item.category = MenuCategory.objects.get(id=category_id, restaurant=item.restaurant)
            except MenuCategory.DoesNotExist:
                item.category = None
        else:
            item.category = None
        item.save()
        messages.success(request, f'"{item.name}" updated!')
        return redirect('food:menu_management')
    categories = item.restaurant.categories.all()
    return render(request, 'partner/edit_menu_item.html', {'item': item, 'categories': categories})


@login_required
def delete_menu_item(request, item_id):
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    item = get_object_or_404(FoodItem, id=item_id)
    if item.restaurant.owner != request.user:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    name = item.name
    item.delete()
    messages.success(request, f'"{name}" deleted from menu.')
    return redirect('food:menu_management')


# ========== AJAX MENU TOGGLE API ==========

@login_required
def api_toggle_item_availability(request, item_id):
    """AJAX: Toggle item availability without page reload"""
    if not request.user.is_restaurant():
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    item = get_object_or_404(FoodItem, id=item_id)
    
    if item.restaurant.owner != request.user:
        return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)
    
    item.is_available = not item.is_available
    item.save()
    
    return JsonResponse({
        'success': True,
        'item_id': item.id,
        'is_available': item.is_available,
        'status_text': 'In Stock' if item.is_available else 'Out of Stock',
    })


@login_required
def add_menu_category(request):
    if not request.user.is_restaurant():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    try:
        restaurant = request.user.restaurant
    except Restaurant.DoesNotExist:
        messages.error(request, 'No restaurant found.')
        return redirect('dashboard')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            MenuCategory.objects.create(restaurant=restaurant, name=name)
            messages.success(request, f'Category "{name}" added!')
    return redirect('food:menu_management')