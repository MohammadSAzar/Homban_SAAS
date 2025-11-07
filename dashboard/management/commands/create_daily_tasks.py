import pytz

from django.core.management.base import BaseCommand

from django.utils import timezone
import jdatetime
from datetime import datetime, time

from dashboard.signals import create_daily_tasks_for_all_agents


class Command(BaseCommand):
    help = 'Create daily tasks for all agents at 01:00 AM Tehran time'

    def handle(self, *args, **options):
        tehran_tz = pytz.timezone('Asia/Tehran')
        now = timezone.now().astimezone(tehran_tz)
        if now.hour == 1:
            today_jalali = jdatetime.date.today().strftime('%Y/%m/%d')

            self.stdout.write(
                self.style.SUCCESS(f'Creating daily tasks for {today_jalali}...')
            )
            create_daily_tasks_for_all_agents()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created daily tasks!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Current hour is {now.hour}. Tasks are created at 01:00 AM.'
                )
            )

