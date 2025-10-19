from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache

from . import models


# --------------------------------- Tasks ---------------------------------
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


