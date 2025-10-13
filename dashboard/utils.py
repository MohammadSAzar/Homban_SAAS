from django.db.models import Count, Q, Prefetch
from django.contrib.contenttypes.models import ContentType
from .models import Announcement, Interaction, InteractionItem, Buyer, Renter, SaleFile, RentFile


def get_unread_announcement_count(user):
    """
    Get count of unread announcements for a user.
    Use this in context processors for displaying in navigation.
    """
    return Announcement.objects.filter(
        visible_to=user,
        is_active=True
    ).exclude(
        viewed_by=user
    ).count()


def get_unread_interaction_count(user):
    """
    Get count of unread received interactions for a user.
    """
    return Interaction.objects.filter(
        receiver=user,
        status='sent'
    ).count()


def get_user_announcement_stats(user):
    """
    Get comprehensive stats for a user's announcements and interactions.
    """
    stats = {
        'announcements_created': Announcement.objects.filter(created_by=user).count(),
        'announcements_unread': get_unread_announcement_count(user),
        'announcements_total_visible': Announcement.objects.filter(
            visible_to=user,
            is_active=True
        ).count(),
        'interactions_sent': Interaction.objects.filter(sender=user).count(),
        'interactions_received': Interaction.objects.filter(receiver=user).count(),
        'interactions_unread': get_unread_interaction_count(user),
        'interactions_pending': Interaction.objects.filter(
            Q(sender=user) | Q(receiver=user),
            status__in=['sent', 'viewed']
        ).count(),
    }
    return stats


def mark_announcement_as_viewed(announcement, user):
    """
    Mark an announcement as viewed by a user.
    """
    if user not in announcement.viewed_by.all():
        announcement.viewed_by.add(user)
        return True
    return False


def mark_interaction_as_viewed(interaction, user):
    """
    Mark an interaction as viewed if the user is the receiver.
    """
    if interaction.receiver == user and interaction.status == 'sent':
        interaction.status = 'viewed'
        from django.utils import timezone
        interaction.viewed_at = timezone.now()
        interaction.save(update_fields=['status', 'viewed_at'])
        return True
    return False


def get_matching_score(obj1, obj2, interaction_type):
    """
    Calculate a matching score between two objects (0-100).
    Higher score means better match.

    Args:
        obj1: First object (e.g., SaleFile)
        obj2: Second object (e.g., Buyer)
        interaction_type: Type of interaction ('buyer_to_sale', 'sale_to_buyer', etc.)

    Returns:
        int: Matching score (0-100)
    """
    score = 0

    if interaction_type in ['buyer_to_sale', 'sale_to_buyer']:
        # Price matching (40 points)
        if hasattr(obj1, 'price_announced') and hasattr(obj2, 'price_announced'):
            price1 = obj1.price_announced
            price2 = obj2.price_announced
        else:
            price1 = obj2.price_announced if hasattr(obj2, 'price_announced') else obj1.price_announced
            price2 = obj1.price_announced if hasattr(obj1, 'price_announced') else obj2.price_announced

        price_diff_percent = abs(price1 - price2) / price1 * 100
        if price_diff_percent <= 5:
            score += 40
        elif price_diff_percent <= 10:
            score += 30
        elif price_diff_percent <= 15:
            score += 20
        else:
            score += 10

        # Area matching (30 points)
        if hasattr(obj1, 'area') and hasattr(obj2, 'area_min'):
            area = obj1.area
            area_min = obj2.area_min
            area_max = obj2.area_max
        else:
            area = obj2.area
            area_min = obj1.area_min
            area_max = obj1.area_max

        if area_min <= area <= area_max:
            score += 30
        elif 0.8 * area_min <= area <= 1.2 * area_max:
            score += 20
        else:
            score += 10

        # Location matching (30 points)
        if hasattr(obj1, 'sub_district') and hasattr(obj2, 'sub_districts'):
            if obj1.sub_district in obj2.sub_districts.all():
                score += 30
            elif obj1.sub_district.district in [sd.district for sd in obj2.sub_districts.all()]:
                score += 15
        elif hasattr(obj2, 'sub_district') and hasattr(obj1, 'sub_districts'):
            if obj2.sub_district in obj1.sub_districts.all():
                score += 30
            elif obj2.sub_district.district in [sd.district for sd in obj1.sub_districts.all()]:
                score += 15

    elif interaction_type in ['renter_to_rent', 'rent_to_renter']:
        # Similar logic for rent calculations
        # Deposit matching (20 points)
        if hasattr(obj1, 'deposit_announced') and hasattr(obj2, 'deposit_announced'):
            deposit1 = obj1.deposit_announced
            deposit2 = obj2.deposit_announced
        else:
            deposit1 = obj2.deposit_announced if hasattr(obj2, 'deposit_announced') else obj1.deposit_announced
            deposit2 = obj1.deposit_announced if hasattr(obj1, 'deposit_announced') else obj2.deposit_announced

        deposit_diff_percent = abs(deposit1 - deposit2) / deposit1 * 100 if deposit1 > 0 else 0
        if deposit_diff_percent <= 10:
            score += 20
        elif deposit_diff_percent <= 20:
            score += 15
        else:
            score += 5

        # Rent matching (20 points)
        if hasattr(obj1, 'rent_announced') and hasattr(obj2, 'rent_announced'):
            rent1 = obj1.rent_announced
            rent2 = obj2.rent_announced
        else:
            rent1 = obj2.rent_announced if hasattr(obj2, 'rent_announced') else obj1.rent_announced
            rent2 = obj1.rent_announced if hasattr(obj1, 'rent_announced') else obj2.rent_announced

        rent_diff_percent = abs(rent1 - rent2) / rent1 * 100 if rent1 > 0 else 0
        if rent_diff_percent <= 10:
            score += 20
        elif rent_diff_percent <= 20:
            score += 15
        else:
            score += 5

        # Area matching (30 points) - similar to sale
        if hasattr(obj1, 'area') and hasattr(obj2, 'area_min'):
            area = obj1.area
            area_min = obj2.area_min
            area_max = obj2.area_max
        else:
            area = obj2.area
            area_min = obj1.area_min
            area_max = obj1.area_max

        if area_min <= area <= area_max:
            score += 30
        elif 0.8 * area_min <= area <= 1.2 * area_max:
            score += 20
        else:
            score += 10

        # Location matching (30 points) - similar to sale
        if hasattr(obj1, 'sub_district') and hasattr(obj2, 'sub_districts'):
            if obj1.sub_district in obj2.sub_districts.all():
                score += 30
            elif obj1.sub_district.district in [sd.district for sd in obj2.sub_districts.all()]:
                score += 15
        elif hasattr(obj2, 'sub_district') and hasattr(obj1, 'sub_districts'):
            if obj2.sub_district in obj1.sub_districts.all():
                score += 30
            elif obj2.sub_district.district in [sd.district for sd in obj1.sub_districts.all()]:
                score += 15

    return min(score, 100)  # Cap at 100


def get_suggestions_with_scores(announcement, user):
    """
    Get suggestions with matching scores for sorting.
    Returns list of tuples: (suggestion_object, score)
    """
    from django.contrib.contenttypes.models import ContentType

    suggestions_with_scores = []
    original_obj = announcement.content_object

    if announcement.announcement_type == 'sale_file':
        buyers = Buyer.objects.filter(
            created_by=user,
            status='acc'
        ).exclude(delete_request='Yes')

        for buyer in buyers:
            score = get_matching_score(original_obj, buyer, 'buyer_to_sale')
            if score >= 40:  # Only include decent matches
                suggestions_with_scores.append((buyer, score))

    elif announcement.announcement_type == 'rent_file':
        renters = Renter.objects.filter(
            created_by=user,
            status='acc'
        ).exclude(delete_request='Yes')

        for renter in renters:
            score = get_matching_score(original_obj, renter, 'renter_to_rent')
            if score >= 40:
                suggestions_with_scores.append((renter, score))

    elif announcement.announcement_type == 'buyer':
        files = SaleFile.objects.filter(
            created_by=user,
            status='acc'
        ).exclude(delete_request='Yes')

        for file_obj in files:
            score = get_matching_score(original_obj, file_obj, 'sale_to_buyer')
            if score >= 40:
                suggestions_with_scores.append((file_obj, score))

    elif announcement.announcement_type == 'renter':
        files = RentFile.objects.filter(
            created_by=user,
            status='acc'
        ).exclude(delete_request='Yes')

        for file_obj in files:
            score = get_matching_score(original_obj, file_obj, 'rent_to_renter')
            if score >= 40:
                suggestions_with_scores.append((file_obj, score))

    # Sort by score descending
    suggestions_with_scores.sort(key=lambda x: x[1], reverse=True)

    return suggestions_with_scores


def bulk_create_interaction(announcement, sender, receiver, selected_ids, message=''):
    """
    Helper function to create an interaction with multiple items efficiently.

    Args:
        announcement: Announcement object
        sender: User sending the interaction
        receiver: User receiving the interaction
        selected_ids: List of IDs of suggested objects
        message: Optional message

    Returns:
        Interaction object
    """
    interaction_type_map = {
        'sale_file': ('buyer_to_sale', ContentType.objects.get_for_model(Buyer)),
        'rent_file': ('renter_to_rent', ContentType.objects.get_for_model(Renter)),
        'buyer': ('sale_to_buyer', ContentType.objects.get_for_model(SaleFile)),
        'renter': ('rent_to_renter', ContentType.objects.get_for_model(RentFile)),
    }

    interaction_type, content_type = interaction_type_map[announcement.announcement_type]

    # Create interaction
    interaction = Interaction.objects.create(
        announcement=announcement,
        sender=sender,
        receiver=receiver,
        interaction_type=interaction_type,
        message=message,
        status='sent'
    )

    # Bulk create interaction items
    items_to_create = []
    model_class = content_type.model_class()

    # Fetch all objects at once
    objects = model_class.objects.filter(pk__in=selected_ids)
    objects_dict = {obj.pk: obj for obj in objects}

    for suggestion_id in selected_ids:
        suggestion_obj = objects_dict.get(int(suggestion_id))
        if suggestion_obj:
            # Determine cached price
            if hasattr(suggestion_obj, 'price_announced'):
                cached_price = suggestion_obj.price_announced
            elif hasattr(suggestion_obj, 'deposit_announced'):
                cached_price = suggestion_obj.deposit_announced
            else:
                cached_price = None

            # Determine cached area
            if hasattr(suggestion_obj, 'area'):
                cached_area = suggestion_obj.area
            elif hasattr(suggestion_obj, 'area_min'):
                cached_area = suggestion_obj.area_min
            else:
                cached_area = None

            items_to_create.append(
                InteractionItem(
                    interaction=interaction,
                    content_type=content_type,
                    object_id=suggestion_obj.pk,
                    cached_price=cached_price,
                    cached_area=cached_area
                )
            )

    # Bulk create all items
    InteractionItem.objects.bulk_create(items_to_create)

    return interaction


def deactivate_old_announcements(days=30):
    """
    Deactivate announcements older than specified days.
    Run this as a periodic task (e.g., with Celery).

    Args:
        days: Number of days after which to deactivate announcements

    Returns:
        int: Number of announcements deactivated
    """
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    count = Announcement.objects.filter(
        is_active=True,
        created_at__lt=cutoff_date
    ).update(is_active=False)

    return count


def get_agent_performance_stats(user, days=30):
    """
    Get performance statistics for an agent over the last N days.

    Args:
        user: Agent user object
        days: Number of days to analyze

    Returns:
        dict: Performance statistics
    """
    from django.utils import timezone
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    stats = {
        # Announcements created by this agent
        'announcements_created': Announcement.objects.filter(
            created_by=user,
            created_at__gte=cutoff_date
        ).count(),

        # Interactions sent by this agent
        'interactions_sent': Interaction.objects.filter(
            sender=user,
            created_at__gte=cutoff_date
        ).count(),

        # Interactions received by this agent
        'interactions_received': Interaction.objects.filter(
            receiver=user,
            created_at__gte=cutoff_date
        ).count(),

        # Average items per interaction sent
        'avg_items_per_interaction': InteractionItem.objects.filter(
            interaction__sender=user,
            interaction__created_at__gte=cutoff_date
        ).count() / max(Interaction.objects.filter(
            sender=user,
            created_at__gte=cutoff_date
        ).count(), 1),

        # Response rate (interactions that were viewed)
        'response_rate': 0,

        # Total items sent
        'total_items_sent': InteractionItem.objects.filter(
            interaction__sender=user,
            interaction__created_at__gte=cutoff_date
        ).count(),
    }

    sent_count = stats['interactions_sent']
    if sent_count > 0:
        viewed_count = Interaction.objects.filter(
            sender=user,
            created_at__gte=cutoff_date,
            status__in=['viewed', 'responded', 'closed']
        ).count()
        stats['response_rate'] = (viewed_count / sent_count) * 100

    return stats


def notify_new_announcement(announcement):
    """
    Send notifications to agents about a new announcement.
    Integrate this with your notification system (email, SMS, push, etc.)

    Args:
        announcement: Announcement object
    """
    from django.core.mail import send_mass_mail
    from django.conf import settings

    agents = announcement.visible_to.all()

    # Prepare email messages
    messages = []
    for agent in agents:
        subject = f'New Announcement: {announcement.get_announcement_type_display()}'
        message = f'''
        Hello {agent.get_full_name()},

        A new {announcement.get_announcement_type_display()} has been approved by {announcement.created_by.get_full_name()}.

        You may have matching suggestions in your inventory.

        View the announcement here: {settings.SITE_URL}/announcements/{announcement.pk}/

        Best regards,
        Real Estate Management System
        '''
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [agent.email]

        messages.append((subject, message, from_email, recipient_list))

    # Send all emails at once
    if messages:
        send_mass_mail(messages, fail_silently=True)


def notify_new_interaction(interaction):
    """
    Send notification to receiver about a new interaction.

    Args:
        interaction: Interaction object
    """
    from django.core.mail import send_mail
    from django.conf import settings

    subject = f'New Suggestions from {interaction.sender.get_full_name()}'
    message = f'''
    Hello {interaction.receiver.get_full_name()},

    {interaction.sender.get_full_name()} has sent you {interaction.items.count()} suggestions 
    for your {interaction.announcement.get_announcement_type_display()}.

    {f"Message: {interaction.message}" if interaction.message else ""}

    View the suggestions here: {settings.SITE_URL}/interactions/{interaction.pk}/

    Best regards,
    Real Estate Management System
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [interaction.receiver.email],
        fail_silently=True
    )


def export_interaction_to_pdf(interaction):
    """
    Export an interaction to PDF format.
    Requires: pip install reportlab

    Args:
        interaction: Interaction object

    Returns:
        BytesIO: PDF file buffer
    """
    from io import BytesIO
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(f"Interaction Details - ID: {interaction.pk}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))

    # Basic info
    info_data = [
        ['From:', interaction.sender.get_full_name()],
        ['To:', interaction.receiver.get_full_name()],
        ['Type:', interaction.get_interaction_type_display()],
        ['Created:', interaction.created_at.strftime('%Y-%m-%d %H:%M')],
        ['Status:', interaction.get_status_display()],
    ]

    if interaction.message:
        info_data.append(['Message:', interaction.message])

    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Items
    items_title = Paragraph("Suggested Items", styles['Heading2'])
    elements.append(items_title)
    elements.append(Spacer(1, 0.2 * inch))

    items_data = [['#', 'Code', 'Price/Deposit', 'Area']]
    for idx, item in enumerate(interaction.items.all(), 1):
        items_data.append([
            str(idx),
            str(item.content_object.code),
            str(item.cached_price) if item.cached_price else 'N/A',
            str(item.cached_area) if item.cached_area else 'N/A'
        ])

    items_table = Table(items_data)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(items_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return buffer


