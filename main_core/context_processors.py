from .models import UserConnection, Notification

def language_context(request):
    """Add language information to the template context."""
    language = getattr(request, 'LANGUAGE', 'en')
    return {
        'LANGUAGE': language,
    }

def notifications(request):
    if request.user.is_authenticated:
        friend_requests = UserConnection.objects.filter(
            connected_to=request.user,
            status='pending'
        ).select_related('user').order_by('-created_at')
        
        message_notifications = Notification.objects.filter(
            user=request.user,
            notification_type='message',
            is_read=False
        ).select_related('sender', 'message').order_by('-created_at')
        
        return {
            'friend_requests': friend_requests,
            'message_notifications': message_notifications,
        }
    return {
        'friend_requests': [],
        'message_notifications': [],
    } 