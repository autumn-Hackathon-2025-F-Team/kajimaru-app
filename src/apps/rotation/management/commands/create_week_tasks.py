from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.rotation.services import create_week_tasks, create_maintenance_tasks

class Command(BaseCommand):
    help = "週ローテ家事のタスクを１週間分まとめて作成するコマンド"

    #実行コマンド: python manage.py create_week_tasks
    def handle(self, *args, **options):
        today = timezone.localdate()
        self.stdout.write(self.style.NOTICE(f"create_week_tasks 実行: {today}"))
        create_week_tasks()
        create_maintenance_tasks(run_date=today)
        self.stdout.write(self.style.SUCCESS("create_week_tasks 完了"))