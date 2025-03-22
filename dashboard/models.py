from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _


class CustomUserModel(AbstractUser):
    TITLE_CHOICES = [
        ('fp', _('File Person')),
        ('cp', _('Customer Person')),
        ('cr', _('Coordinator')),
        ('bs', _('Boss')),
    ]
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True, null=True, verbose_name=_('Title'))
    email = models.EmailField(unique=False, blank=True, null=True)

    REQUIRED_FIELDS = []


