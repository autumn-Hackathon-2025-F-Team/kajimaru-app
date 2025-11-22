from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.user.models import Users
from django.utils import timezone

# WEEKDAY_FLAGS = [
#     (1, '月曜日'),
#     (2, '火曜日'),
#     (4, '水曜日'),
#     (8, '木曜日'),
#     (16, '金曜日'),
#     (32, '土曜日'),
#     (64, '日曜日'),
# ]
WEEKDAY_FLAGS = [
    (1, '月'),
    (2, '火'),
    (4, '水'),
    (8, '木'),
    (16, '金'),
    (32, '土'),
    (64, '日'),
]

class TaskList(models.Model):
    task_name = models.CharField(max_length=50, verbose_name="家事名")
    frequency = models.PositiveSmallIntegerField(verbose_name="頻度(曜日)",
                help_text="ビットフラグで複数曜日を表現(例: 月・水・金 = 1+4+16=21)",default=0,validators=[MinValueValidator(0), MaxValueValidator(127)])
    homemakers = models.ManyToManyField(Users, verbose_name="担当者", related_name="task_lists", blank=True)
    weight = models.PositiveIntegerField(verbose_name="重み", default=1,validators=[MinValueValidator(1), MaxValueValidator(5)],help_text="1=簡単, 5=大変")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_weekday_labels(self):
        labels = []
        for bit, label in WEEKDAY_FLAGS:
            if self.frequency & bit:
                labels.append(label)
        return ", ".join(labels) if labels else "曜日未設定"

    def __str__(self):
        names = ", ".join(h.display_name for h in self.homemakers.all()) or "担当者未設定"
        return f"{self.task_name}({self.get_weekday_labels()} / {names})"
    # def __str__(self):
    #     return self.task_name
class Maintenance(models.Model):
    target_name = models.CharField(max_length=20,verbose_name="メンテナンス名")
    homemakers = models.ManyToManyField(Users, verbose_name="担当者", related_name="maintenance_task_lists", blank=True)  
    last_date = models.DateTimeField(verbose_name="前回実施日")
    next_date = models.DateTimeField(verbose_name="次回予定日")
    is_choice = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        names = ", ".join(h.display_name for h in self.homemakers.all()) or "担当者未設定"
        return f"{self.target_name}({names})"
    # def __str__(self):
    #     return self.target_name
class Task(models.Model):
    task_list = models.ForeignKey(TaskList, on_delete=models.SET_NULL,related_name="tasks",null=True,blank=True)
    maintenance = models.ForeignKey(Maintenance, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True)
    daily = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=10)
    substitute = models.CharField(max_length=10, blank=True)
    is_completed = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            user_name = self.user.display_name
        else:
            user_name = "未設定"

        base = f"{self.role}({user_name})"
        if self.substitute:
            return f"{base} → {self.substitute}代行"
        return base
