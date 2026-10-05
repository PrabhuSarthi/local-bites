from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import GroceryStore, GroceryCategory, GroceryProduct, GroceryOrder, GroceryOrderItem


def _build_cart_payload(request):
    """Helper: build full grocery cart data for API responses"""
    cart = request.session.get('grocery_cart', {})
    store_id = request.session.get('grocery_cart_store')
    
    items_data = []
    subtotal = 0
    store_name = None
    
    if cart and store_id:
        try:
            store = GroceryStore.objects.get(id=store_id)
            store_name = store.name
            for product_id_str, qty in cart.items():
                try:
                    product = GroceryProduct.objects.get(id=int(product_id_str))
                    item_total = float(product.price) * qty
                    items_data.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'unit': product.get_unit_display(),
                        'quantity': qty,
                        'subtotal': round(item_total, 2),
                    })
                    subtotal += item_total
                except GroceryProduct.DoesNotExist:
                    pass
        except GroceryStore.DoesNotExist:
            pass
    
    return {
        'items': items_data,
        'subtotal': round(subtotal, 2),
        'store_name': store_name,
        'cart_count': sum(cart.values()) if cart else 0,
    }


def store_list(request):
    """Public grocery store listing"""
    stores = GroceryStore.objects.filter(is_active=True, is_approved=True)
    
    search = request.GET.get('q', '')
    if search:
        stores = stores.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    context = {
        'stores': stores,
        'search': search,
    }
    return render(request, 'grocery/store_list.html', context)


def store_detail(request, store_id):
    """Store detail + products"""
    store = get_object_or_404(GroceryStore, id=store_id, is_active=True)
    categories = store.categories.all().prefetch_related('products')
    
    cart = request.session.get('grocery_cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    initial_cart = _build_cart_payload(request)
    
    context = {
        'store': store,
        'categories': categories,
        'cart_count': cart_count,
        'cart': cart,
        'initial_cart': initial_cart,
    }
    return render(request, 'grocery/store_detail.html', context)


# ==================== AJAX CART APIS ====================

def api_add_to_cart(request, product_id):
    """AJAX: Add product to cart"""
    product = get_object_or_404(GroceryProduct, id=product_id)
    
    cart = request.session.get('grocery_cart', {})
    cart_store = request.session.get('grocery_cart_store', None)
    
    cart_cleared = False
    if cart_store and cart_store != product.store.id:
        cart = {}
        cart_cleared = True
    
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    
    request.session['grocery_cart'] = cart
    request.session['grocery_cart_store'] = product.store.id
    request.session.modified = True
    
    payload = _build_cart_payload(request)
    payload.update({
        'success': True,
        'item_id': product.id,
        'item_count': cart[product_id_str],
        'cart_cleared': cart_cleared,
    })
    return JsonResponse(payload)


def api_decrease_cart(request, product_id):
    """AJAX: Decrease product quantity"""
    product = get_object_or_404(GroceryProduct, id=product_id)
    
    cart = request.session.get('grocery_cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str] -= 1
        if cart[product_id_str] <= 0:
            del cart[product_id_str]
    
    request.session['grocery_cart'] = cart
    request.session.modified = True
    
    if not cart:
        request.session.pop('grocery_cart_store', None)
    
    payload = _build_cart_payload(request)
    payload.update({
        'success': True,
        'item_id': product.id,
        'item_count': cart.get(product_id_str, 0),
    })
    return JsonResponse(payload)


def api_remove_from_cart(request, product_id):
    """AJAX: Remove product completely"""
    product_id_str = str(product_id)
    
    cart = request.session.get('grocery_cart', {})
    if product_id_str in cart:
        del cart[product_id_str]
    
    request.session['grocery_cart'] = cart
    request.session.modified = True
    
    if not cart:
        request.session.pop('grocery_cart_store', None)
    
    payload = _build_cart_payload(request)
    payload.update({
        'success': True,
        'item_id': int(product_id),
        'item_count': 0,
    })
    return JsonResponse(payload)


# ==================== END AJAX APIS ====================


def add_to_cart(request, product_id):
    """Legacy: Add to cart"""
    product = get_object_or_404(GroceryProduct, id=product_id)
    
    cart = request.session.get('grocery_cart', {})
    cart_store = request.session.get('grocery_cart_store', None)
    
    if cart_store and cart_store != product.store.id:
        cart = {}
        messages.info(request, f'Cart cleared. Now shopping from {product.store.name}')
    
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + 1
    
    request.session['grocery_cart'] = cart
    request.session['grocery_cart_store'] = product.store.id
    request.session.modified = True
    
    messages.success(request, f'Added {product.name} to cart')
    return redirect('grocery:store_detail', store_id=product.store.id)


def cart_view(request):
    """View cart"""
    cart = request.session.get('grocery_cart', {})
    store_id = request.session.get('grocery_cart_store')
    
    items = []
    subtotal = 0
    store = None
    
    if cart and store_id:
        store = get_object_or_404(GroceryStore, id=store_id)
        for product_id_str, qty in cart.items():
            try:
                product = GroceryProduct.objects.get(id=int(product_id_str))
                item_total = float(product.price) * qty
                items.append({
                    'product': product,
                    'quantity': qty,
                    'total': item_total,
                })
                subtotal += item_total
            except GroceryProduct.DoesNotExist:
                pass
    
    delivery_fee = float(store.delivery_fee) if store else 0
    tax = round(subtotal * 0.05, 2)
    total = subtotal + delivery_fee + tax
    
    context = {
        'items': items,
        'store': store,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'tax': tax,
        'total': total,
        'cart_count': sum(cart.values()) if cart else 0,
    }
    return render(request, 'grocery/cart.html', context)


def update_cart(request, product_id):
    """Update quantity"""
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = request.session.get('grocery_cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            if action == 'increase':
                cart[product_id_str] += 1
            elif action == 'decrease':
                cart[product_id_str] -= 1
                if cart[product_id_str] <= 0:
                    del cart[product_id_str]
            elif action == 'remove':
                del cart[product_id_str]
        
        request.session['grocery_cart'] = cart
        request.session.modified = True
        
        if not cart:
            request.session.pop('grocery_cart_store', None)
    
    return redirect('grocery:cart')


@login_required
def checkout_view(request):
    """Checkout page"""
    cart = request.session.get('grocery_cart', {})
    store_id = request.session.get('grocery_cart_store')
    
    if not cart or not store_id:
        messages.warning(request, 'Your cart is empty')
        return redirect('grocery:store_list')
    
    store = get_object_or_404(GroceryStore, id=store_id)
    
    items = []
    subtotal = 0
    for product_id_str, qty in cart.items():
        try:
            product = GroceryProduct.objects.get(id=int(product_id_str))
            items.append({'product': product, 'quantity': qty, 'total': float(product.price) * qty})
            subtotal += float(product.price) * qty
        except GroceryProduct.DoesNotExist:
            pass
    
    delivery_fee = float(store.delivery_fee)
    tax = round(subtotal * 0.05, 2)
    total = subtotal + delivery_fee + tax
    
    if request.method == 'POST':
        order = GroceryOrder.objects.create(
            customer=request.user,
            store=store,
            delivery_address=request.POST.get('address', request.user.address or ''),
            phone=request.POST.get('phone', request.user.phone or ''),
            delivery_slot=request.POST.get('delivery_slot', ''),
            special_instructions=request.POST.get('instructions', ''),
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax=tax,
            total=total,
            payment_method=request.POST.get('payment_method', 'COD'),
        )
        
        for item_data in items:
            GroceryOrderItem.objects.create(
                order=order,
                product=item_data['product'],
                quantity=item_data['quantity'],
                price=item_data['product'].price,
            )
            item_data['product'].stock -= item_data['quantity']
            item_data['product'].times_ordered += item_data['quantity']
            item_data['product'].save()
        
        # Notify store owner
        from notifications.models import Notification
        customer_name = request.user.get_full_name()
        if not customer_name:
            customer_name = request.user.username
        
        Notification.objects.create(
            user=store.owner,
            title='🛒 New Grocery Order!',
            message=f'Order #{order.order_number} received from {customer_name} · ₹{order.total}',
            notification_type='order',
            link=f'/grocery/store-orders/',
            icon='🛒',
        )
        
        request.session.pop('grocery_cart', None)
        request.session.pop('grocery_cart_store', None)
        
        messages.success(request, f'Order placed! Order #{order.order_number}')
        return redirect('grocery:order_confirmation', order_id=order.id)
    
    context = {
        'items': items,
        'store': store,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'tax': tax,
        'total': total,
    }
    return render(request, 'grocery/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    """Order confirmation"""
    order = get_object_or_404(GroceryOrder, id=order_id, customer=request.user)
    return render(request, 'grocery/order_confirmation.html', {'order': order})


@login_required
def my_orders(request):
    """Customer's grocery orders"""
    orders = GroceryOrder.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'grocery/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Single order view - ROLE AWARE"""
    order = get_object_or_404(GroceryOrder, id=order_id)
    
    if request.user.is_customer() and order.customer != request.user:
        messages.error(request, 'Access denied')
        return redirect('grocery:store_list')
    
    if request.user.is_grocery() and order.store.owner != request.user:
        messages.error(request, 'Access denied')
        return redirect('grocery:store_list')
    
    if request.user.is_grocery():
        return render(request, 'grocery/order_detail_restaurant.html', {'order': order})
    else:
        return render(request, 'grocery/order_detail.html', {'order': order})


# ========== GROCERY OWNER VIEWS ==========

@login_required
def store_orders(request):
    """Grocery owner sees their orders"""
    if not request.user.is_grocery():
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    try:
        store = request.user.grocery_store
    except GroceryStore.DoesNotExist:
        messages.error(request, 'No store found.')
        return redirect('dashboard')
    
    orders = GroceryOrder.objects.filter(store=store).order_by('-created_at')
    low_stock = store.products.filter(stock__lt=10).order_by('stock')
    
    context = {
        'store': store,
        'orders': orders,
        'low_stock': low_stock,
    }
    return render(request, 'grocery/store_orders.html', context)


@login_required
def update_order_status(request, order_id):
    """Update order status"""
    order = get_object_or_404(GroceryOrder, id=order_id)
    
    if not request.user.is_grocery() or order.store.owner != request.user:
        messages.error(request, 'Access denied')
        return redirect('dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(GroceryOrder.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'delivered':
                from django.utils import timezone
                order.delivered_at = timezone.now()
            order.save()
            
            from notifications.models import Notification
            status_icons = {
                'confirmed': '✅',
                'packing': '📦',
                'out_for_delivery': '🛵',
                'delivered': '🎉',
                'cancelled': '❌',
            }
            Notification.objects.create(
                user=order.customer,
                title=f'{status_icons.get(new_status, "📦")} Grocery Order {order.get_status_display()}',
                message=f'Your grocery order #{order.order_number} from {order.store.name} is now {order.get_status_display().lower()}',
                notification_type='order',
                link=f'/grocery/orders/{order.id}/',
                icon=status_icons.get(new_status, '📦'),
            )
            
            messages.success(request, f'Order #{order.order_number} status updated')
    
    referer = request.META.get('HTTP_REFERER', '')
    if f'/grocery/orders/{order_id}/' in referer:
        return redirect('grocery:order_detail', order_id=order.id)
    return redirect('grocery:store_orders')