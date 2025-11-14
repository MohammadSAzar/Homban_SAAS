from django.db.models import Q, Count
from django.core.cache import cache

from .models import Announcement, Interaction, NotifiedTask, ChatRoom


def notification_counts(request):
    if request.user.is_authenticated:
        # Count unread announcements
        unread_announcements_count = Announcement.objects.filter(
            visible_to=request.user,
            is_active=True
        ).exclude(
            viewed_by=request.user
        ).count()

        # Count unread received interactions
        unread_interactions_count = Interaction.objects.filter(
            receiver=request.user,
            status='sent'
        ).count()

        # Count pending notified tasks (both types)
        pending_tasks_count = NotifiedTask.objects.filter(
            agent=request.user,
            status='waiting'
        ).count()

        # Separate counts for task types
        announcement_suggestion_tasks = NotifiedTask.objects.filter(
            agent=request.user,
            task_type='announcement_suggestions',
            status='waiting'
        ).count()

        received_interaction_tasks = NotifiedTask.objects.filter(
            agent=request.user,
            task_type='received_interaction',
            status='waiting'
        ).count()

        # Total unread (for main menu badge)
        total_unread = unread_announcements_count + unread_interactions_count

        return {
            'unread_announcements_count': unread_announcements_count,
            'unread_interactions_count': unread_interactions_count,
            'pending_tasks_count': pending_tasks_count,
            'announcement_suggestion_tasks_count': announcement_suggestion_tasks,
            'received_interaction_tasks_count': received_interaction_tasks,
            'total_unread_count': total_unread,
            'has_unread_notifications': total_unread > 0,
            'has_pending_tasks': pending_tasks_count > 0,
        }

    return {
        'unread_announcements_count': 0,
        'unread_interactions_count': 0,
        'pending_tasks_count': 0,
        'announcement_suggestion_tasks_count': 0,
        'received_interaction_tasks_count': 0,
        'total_unread_count': 0,
        'has_unread_notifications': False,
        'has_pending_tasks': False,
    }


def chat_notifications(request):
    if request.user.is_authenticated:
        cache_key = f'chat_notifications_{request.user.pk}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return cached_data

        total_unread_chats = ChatRoom.objects.filter(
            participants=request.user
        ).annotate(
            unread=Count(
                'messages',
                filter=~Q(messages__read_by=request.user) & ~Q(messages__sender=request.user)
            )
        ).aggregate(total=Count('id', filter=Q(unread__gt=0)))['total'] or 0

        unread_private = ChatRoom.objects.filter(
            room_type='private',
            participants=request.user
        ).annotate(
            unread=Count(
                'messages',
                filter=~Q(messages__read_by=request.user) & ~Q(messages__sender=request.user)
            )
        ).filter(unread__gt=0).count()

        # Group unread count
        group_room = ChatRoom.objects.filter(
            room_type='group',
            participants=request.user
        ).first()

        unread_group = 0
        if group_room:
            unread_group = group_room.messages.exclude(
                read_by=request.user
            ).exclude(
                sender=request.user
            ).count()

        # Channel unread count
        channel_room = ChatRoom.objects.filter(
            room_type='channel',
            participants=request.user
        ).first()

        unread_channel = 0
        if channel_room:
            unread_channel = channel_room.messages.exclude(
                read_by=request.user
            ).exclude(
                sender=request.user
            ).count()

        data = {
            'unread_private_chats': unread_private,
            'unread_group_messages': unread_group,
            'unread_channel_messages': unread_channel,
            'total_unread_chats': total_unread_chats,
            'has_unread_chats': total_unread_chats > 0,
        }

        # Cache for 5 minutes
        cache.set(cache_key, data, 300)

        return data

    return {
        'unread_private_chats': 0,
        'unread_group_messages': 0,
        'unread_channel_messages': 0,
        'total_unread_chats': 0,
        'has_unread_chats': False,
    }


