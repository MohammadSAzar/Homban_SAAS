import pytz

from django.db.models.signals import post_save, pre_save
from django.db.models import Q, F, PositiveBigIntegerField
from django.db.models.functions import Cast

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.dispatch import receiver

import jdatetime
from datetime import datetime, time

from . import models


# --------------------------------- BossTasks ---------------------------------
@receiver(post_save, sender=models.SaleFile)
def boss_task_sale_file(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_sale_file=instance, type='sf')


@receiver(post_save, sender=models.RentFile)
def boss_task_rent_file(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_rent_file=instance, type='rf')


@receiver(post_save, sender=models.Buyer)
def boss_task_buyer(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_buyer=instance, type='by')


@receiver(post_save, sender=models.Renter)
def boss_task_renter(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_renter=instance, type='rt')


@receiver(post_save, sender=models.Person)
def boss_task_person(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_person=instance, type='ps')


@receiver(post_save, sender=models.Session)
def boss_task_session(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_session=instance, type='ss')


# --------------------------------- Announcements ---------------------------------
def create_announcement_for_agents(instance, announcement_type):
    all_agents = models.CustomUserModel.objects.filter(
        is_active=True
    ).exclude(
        pk=instance.created_by.pk
    )
    if all_agents.exists():
        announcement = models.Announcement.objects.create(
            content_object=instance,
            created_by=instance.created_by,
            announcement_type=announcement_type
        )
        announcement.visible_to.set(all_agents)

        for agent in all_agents:
            cache.delete(f'notifications_{agent.pk}')

        return announcement
    return None


@receiver(pre_save, sender=models.SaleFile)
def check_sale_file_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = models.SaleFile.objects.get(pk=instance.pk)
            instance._status_changed_to_acc = (
                    old_instance.status != 'acc' and instance.status == 'acc'
            )
        except models.SaleFile.DoesNotExist:
            instance._status_changed_to_acc = False
    else:
        instance._status_changed_to_acc = instance.status == 'acc'


@receiver(post_save, sender=models.SaleFile)
def create_announcement_for_sale_file(sender, instance, created, **kwargs):
    if hasattr(instance, '_status_changed_to_acc') and instance._status_changed_to_acc:
        create_announcement_for_agents(instance, 'sf')


@receiver(pre_save, sender=models.RentFile)
def check_rent_file_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = models.RentFile.objects.get(pk=instance.pk)
            instance._status_changed_to_acc = (
                    old_instance.status != 'acc' and instance.status == 'acc'
            )
        except models.RentFile.DoesNotExist:
            instance._status_changed_to_acc = False
    else:
        instance._status_changed_to_acc = instance.status == 'acc'


@receiver(post_save, sender=models.RentFile)
def create_announcement_for_rent_file(sender, instance, created, **kwargs):
    if hasattr(instance, '_status_changed_to_acc') and instance._status_changed_to_acc:
        create_announcement_for_agents(instance, 'rf')


@receiver(pre_save, sender=models.Buyer)
def check_buyer_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = models.Buyer.objects.get(pk=instance.pk)
            instance._status_changed_to_acc = (
                    old_instance.status != 'acc' and instance.status == 'acc'
            )
        except models.Buyer.DoesNotExist:
            instance._status_changed_to_acc = False
    else:
        instance._status_changed_to_acc = instance.status == 'acc'


@receiver(post_save, sender=models.Buyer)
def create_announcement_for_buyer(sender, instance, created, **kwargs):
    if hasattr(instance, '_status_changed_to_acc') and instance._status_changed_to_acc:
        create_announcement_for_agents(instance, 'by')


@receiver(pre_save, sender=models.Renter)
def check_renter_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = models.Renter.objects.get(pk=instance.pk)
            instance._status_changed_to_acc = (
                    old_instance.status != 'acc' and instance.status == 'acc'
            )
        except models.Renter.DoesNotExist:
            instance._status_changed_to_acc = False
    else:
        instance._status_changed_to_acc = instance.status == 'acc'


@receiver(post_save, sender=models.Renter)
def create_announcement_for_renter(sender, instance, created, **kwargs):
    if hasattr(instance, '_status_changed_to_acc') and instance._status_changed_to_acc:
        create_announcement_for_agents(instance, 'rt')


# --------------------------------- NotifiedTasks ---------------------------------
@receiver(post_save, sender=models.Announcement)
def create_announcement_suggestion_task(sender, instance, created, **kwargs):
    if not created:
        return

    announcement = instance
    agents_with_suggestions = announcement.get_agents_with_suggestions()
    for agent in agents_with_suggestions:
        models.NotifiedTask.objects.get_or_create(
            agent=agent,
            task_type='announcement_suggestions',
            related_announcement=announcement,
            defaults={
                'status': 'waiting'
            }
        )


@receiver(post_save, sender=models.InteractionItem)
def create_received_interaction_task(sender, instance, created, **kwargs):
    if not created:
        return

    interaction_item = instance
    interaction = interaction_item.interaction
    receiver = interaction.receiver

    models.NotifiedTask.objects.create(
        agent=receiver,
        task_type='received_interaction',
        related_interaction_item=interaction_item,
        content_type=interaction_item.content_type,
        object_id=interaction_item.object_id,
        status='waiting'
    )


@receiver(post_save, sender=models.Interaction)
def mark_announcement_suggestion_tasks_done(sender, instance, created, **kwargs):
    if not created:
        return

    interaction = instance
    announcement = interaction.announcement
    sender_agent = interaction.sender
    models.NotifiedTask.objects.filter(
        agent=sender_agent,
        task_type='announcement_suggestions',
        related_announcement=announcement,
        status='waiting'
    ).update(status='done')


@receiver(post_save, sender=models.Report)
def update_daily_task_status_on_report_save(sender, instance, created, **kwargs):
    report = instance
    if report.agent and report.date:
        daily_status, created = models.DailyTaskStatus.objects.get_or_create(
            agent=report.agent,
            date=report.date
        )
        daily_status.update_from_report(report)


@receiver(post_save, sender=models.ReportItem)
def update_daily_task_status_on_report_item_save(sender, instance, created, **kwargs):
    report_item = instance
    if report_item.report and report_item.report.agent and report_item.report.date:
        daily_status, created = models.DailyTaskStatus.objects.get_or_create(
            agent=report_item.report.agent,
            date=report_item.report.date
        )
        daily_status.update_from_report(report_item.report)


def get_agents_with_suggestions(announcement_instance):
    agents_with_suggestions = []
    creator = announcement_instance.created_by
    if announcement_instance.announcement_type == 'sf':
        sale_file = announcement_instance.content_object
        matching_buyers = models.Buyer.objects.filter(
            status='acc',
            budget_announced__gt=0.9 * sale_file.price_announced,
            budget_announced__lt=1.1 * sale_file.price_announced,
            area_min__lt=1.2 * sale_file.area,
            area_max__gt=0.8 * sale_file.area
        ).exclude(
            delete_request='Yes'
        ).exclude(
            created_by=creator
        ).values_list('created_by', flat=True).distinct()
        agents_with_suggestions = list(matching_buyers)

    elif announcement_instance.announcement_type == 'rf':
        rent_file = announcement_instance.content_object
        base_queryset = models.Renter.objects.annotate(
            deposit_total_calc=Cast(
                F('deposit_announced') + (100 * F('rent_announced') / 3),
                PositiveBigIntegerField()
            )
        ).exclude(
            delete_request='Yes'
        ).exclude(
            created_by=creator
        )
        non_convertable = base_queryset.filter(
            status='acc',
            convertable='isnt',
            deposit_announced__gt=0.8 * rent_file.deposit_announced,
            deposit_announced__lt=1.2 * rent_file.deposit_announced,
            rent_announced__gt=0.8 * rent_file.rent_announced,
            rent_announced__lt=1.2 * rent_file.rent_announced,
            area_min__lt=1.2 * rent_file.area,
            area_max__gt=0.8 * rent_file.area
        )
        rent_total_min = 0.8 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))
        rent_total_max = 1.2 * (rent_file.deposit_announced + 100 * (rent_file.rent_announced / 3))
        convertable = base_queryset.filter(
            status='acc',
            convertable='is',
            deposit_total_calc__gt=rent_total_min,
            deposit_total_calc__lt=rent_total_max,
            area_min__lt=1.2 * rent_file.area,
            area_max__gt=0.8 * rent_file.area
        )
        matching_renters = (non_convertable | convertable).values_list('created_by', flat=True).distinct()
        agents_with_suggestions = list(matching_renters)

    elif announcement_instance.announcement_type == 'by':
        buyer = announcement_instance.content_object
        price_min = 0.9 * buyer.budget_announced
        price_max = 1.1 * buyer.budget_announced
        area_min = 0.8 * buyer.area_min
        area_max = 1.2 * buyer.area_max
        query = models.SaleFile.objects.filter(
            status='acc',
            price_announced__gt=price_min,
            price_announced__lt=price_max,
            area__gt=area_min,
            area__lt=area_max
        ).exclude(
            delete_request='Yes'
        ).exclude(
            created_by=creator
        )
        matching_files = query.values_list('created_by', flat=True).distinct()
        agents_with_suggestions = list(matching_files)

    elif announcement_instance.announcement_type == 'rt':
        renter = announcement_instance.content_object
        deposit_min = 0.8 * renter.deposit_announced
        deposit_max = 1.2 * renter.deposit_announced
        rent_min = 0.8 * renter.rent_announced
        rent_max = 1.2 * renter.rent_announced
        area_min = 0.8 * renter.area_min
        area_max = 1.2 * renter.area_max
        renter_total_min = 0.8 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))
        renter_total_max = 1.2 * (renter.deposit_announced + 100 * (renter.rent_announced / 3))

        base_queryset = models.RentFile.objects.annotate(
            deposit_total_calc=Cast(
                F('deposit_announced') + (100 * F('rent_announced') / 3),
                PositiveBigIntegerField()
            )
        ).exclude(
            delete_request='Yes'
        ).exclude(
            created_by=creator
        )

        non_convertable = base_queryset.filter(
            status='acc',
            convertable='isnt',
            deposit_announced__gt=deposit_min,
            deposit_announced__lt=deposit_max,
            rent_announced__gt=rent_min,
            rent_announced__lt=rent_max,
            area__gt=area_min,
            area__lt=area_max
        )

        convertable = base_queryset.filter(
            status='acc',
            convertable='is',
            deposit_total_calc__gt=renter_total_min,
            deposit_total_calc__lt=renter_total_max,
            area__gt=area_min,
            area__lt=area_max
        )

        query = (non_convertable | convertable).distinct()
        matching_files = query.values_list('created_by', flat=True).distinct()
        agents_with_suggestions = list(matching_files)

    return models.CustomUserModel.objects.filter(id__in=agents_with_suggestions)


