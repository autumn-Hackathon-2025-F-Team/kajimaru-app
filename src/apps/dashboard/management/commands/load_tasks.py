from django.core.management.base import BaseCommand
from apps.dashboard.models import TaskList

class Command(BaseCommand):
	help = 'デフォルトタスクを一括投入します'
	
	def handle(self, *args, **options):
		
		task_data = [
			TaskList(task_name="料理(朝)/お弁当",frequency="127",weight="5"),
			TaskList(task_name="料理(昼)",frequency="96",weight="3"),
			TaskList(task_name="料理(夜)",frequency="127",weight="5"),
			TaskList(task_name="食器洗い",frequency="127",weight="3"),
			TaskList(task_name="トイレ掃除",frequency="64",weight="2"),
			TaskList(task_name="お風呂掃除",frequency="127",weight="2"),
			TaskList(task_name="ごみ捨て",frequency="127",weight="1"),
			TaskList(task_name="玄関掃除",frequency="64",weight="2"),
			TaskList(task_name="洗濯畳む",frequency="127",weight="3"),
			TaskList(task_name="洗濯(干すまで)",frequency="127",weight="4"),
			TaskList(task_name="掃除(全部屋)",frequency="32",weight="3"),
		]
		
		try:
			TaskList.objects.all().delete()
			
			TaskList.objects.bulk_create(task_data, ignore_conflicts=True)
			
			self.stdout.write(
				self.style.SUCCESS(f'{len(task_data)}件のデフォルトタスクを投入しました')
			)
		
		except Exception as e:
			self.stdout.write(
				self.style.ERROR(f'エラーが発生しました: {e}')
			)