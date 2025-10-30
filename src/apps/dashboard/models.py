from django.db import models
from apps.user.models import Users
from django.utils import timezone
class Task(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    daily = models.DateTimeField(default=timezone.now)
    role = models.CharField(max_length=10)
    substitute = models.CharField(max_length=10, blank=True)
    is_completed = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.substitute:
            return f"{self.role}{self.substitute}"
        return self.role

class TaskList(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=50)
    frequency = models.PositiveIntegerField()
    homemaker = models.CharField(max_length=10)
    weight = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_name}{self.homemaker}"

class Maintenance(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    target_name = models.CharField(max_length=20)
    last_date = models.DateTimeField()
    next_date = models.DateTimeField()
    is_choice = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.target_name
