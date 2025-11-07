from .models import Announcement, Interaction, NotifiedTask


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


