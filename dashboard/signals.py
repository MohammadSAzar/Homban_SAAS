from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models


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


@receiver(post_save, sender=models.Visit)
def boss_task_visit(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_visit=instance, type='vs')


@receiver(post_save, sender=models.Session)
def boss_task_session(sender, instance, created, **kwargs):
    if created:
        models.TaskBoss.objects.create(new_session=instance, type='ss')



