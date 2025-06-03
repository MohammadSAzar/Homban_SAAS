from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaleFile, RentFile, Buyer, Renter, Person, Task, TaskBoss


@receiver(post_save, sender=SaleFile)
def boss_task_sale_file(sender, instance, created, **kwargs):
    if created:
        TaskBoss.objects.create(new_sale_file=instance, type='sf')


@receiver(post_save, sender=RentFile)
def boss_task_rent_file(sender, instance, created, **kwargs):
    if created:
        TaskBoss.objects.create(new_rent_file=instance, type='rf')


@receiver(post_save, sender=Buyer)
def boss_task_buyer(sender, instance, created, **kwargs):
    if created:
        TaskBoss.objects.create(new_buyer=instance, type='by')


@receiver(post_save, sender=Renter)
def boss_task_renter(sender, instance, created, **kwargs):
    if created:
        TaskBoss.objects.create(new_renter=instance, type='rt')


@receiver(post_save, sender=Person)
def boss_task_person(sender, instance, created, **kwargs):
    if created:
        TaskBoss.objects.create(new_person=instance, type='ps')





