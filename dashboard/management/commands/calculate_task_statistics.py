from django.core.management.base import BaseCommand

from django.utils import timezone
import jdatetime
from datetime import timedelta

from dashboard.models import NotifiedTaskStats, CustomUserModel


class Command(BaseCommand):
    help = 'Calculate task statistics for all agents'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            default='daily',
            choices=['daily', 'weekly', 'monthly'],
            help='Period type to calculate'
        )

    def handle(self, *args, **options):
        period_type = options['period']
        today = jdatetime.date.today()
        if period_type == 'daily':
            target_date = today - timedelta(days=1)
            period_start = period_end = target_date.strftime('%Y/%m/%d')

