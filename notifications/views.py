from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification


@login_required
def notification_list(request):
    """View all notifications - role-aware template"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by type
    notif_type = request.GET.get('type', '')
    if notif_type:
        notifications = notifications.filter(notification_type=notif_type)
    
    # Counts
    total = Notification.objects.filter(user=request.user).count()
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    
    order_count = Notification.objects.filter(user=request.user, notification_type='order').count()
    ride_count = Notification.objects.filter(user=request.user, notification_type='ride').count()
    system_count = Notification.objects.filter(user=request.user, notification_type='system').count()
    promo_count = Notification.objects.filter(user=request.user, notification_type='promo').count()
    
    context = {
        'notifications': notifications,
        'notif_type': notif_type,
        'total': total,
        'unread': unread,
        'order_count': order_count,
        'ride_count': ride_count,
        'system_count': system_count,
        'promo_count': promo_count,
    }
    
    # Role-aware template
    if request.user.is_customer():
        return render(request, 'notifications/list_customer.html', context)
    else:
        return render(request, 'notifications/list.html', context)


@login_required
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    if notification.link:
        return redirect(notification.link)
    
    return redirect('/notifications/')


@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('/notifications/')


@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return redirect('/notifications/')


@login_required
def clear_all(request):
    """Delete all read notifications"""
    Notification.objects.filter(user=request.user, is_read=True).delete()
    return redirect('/notifications/')


@login_required
def unread_count(request):
    """API endpoint - get unread count"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})