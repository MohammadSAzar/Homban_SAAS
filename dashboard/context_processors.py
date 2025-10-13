from django.core.cache import cache
from .models import Announcement, Interaction


def notification_counts(request):
    if request.user.is_authenticated:
        cache_key = f'notifications_{request.user.pk}'
        counts = cache.get(cache_key)

        if counts is None:
            unread_announcements_count = Announcement.objects.filter(
                visible_to=request.user,
                is_active=True
            ).exclude(
                viewed_by=request.user
            ).count()

            unread_interactions_count = Interaction.objects.filter(
                receiver=request.user,
                status='sent'
            ).count()

            total_unread = unread_announcements_count + unread_interactions_count
            counts = {
                'unread_announcements_count': unread_announcements_count,
                'unread_interactions_count': unread_interactions_count,
                'total_unread_count': total_unread,
                'has_unread_notifications': total_unread > 0,
            }
            cache.set(cache_key, counts, 300)
        return counts

    return {
        'unread_announcements_count': 0,
        'unread_interactions_count': 0,
        'total_unread_count': 0,
        'has_unread_notifications': False,
    }



