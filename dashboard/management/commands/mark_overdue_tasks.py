from django.core.management.base import BaseCommand

from django.utils import timezone
import jdatetime

from dashboard.models import NotifiedTask


class Command(BaseCommand):
    help = 'Mark overdue tasks as delayed'

    def handle(self, *args, **options):
        today = jdatetime.date.today().strftime('%Y/%m/%d')
        overdue_tasks = NotifiedTask.objects.filter(
            status='waiting',
            date__lt=today
        )
        count = overdue_tasks.update(status='delayed')
        self.stdout.write(
            self.style.SUCCESS(f'Marked {count} tasks as delayed')
        )

