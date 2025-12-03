from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from apps.user.models import Household

FREQ_CHOICES = (
    ('6m', '半年'),
    ('12m', '年1'),
    ('24m', '年2'),
)

class MaintenanceItem(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    is_appliance = models.BooleanField(default=True)     # True=家電, False=設備
    target_name = models.CharField(max_length=50)
    frequency = models.CharField(max_length=3, choices=FREQ_CHOICES)
    last_date = models.DateField()
    next_date = models.DateField()
    task_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['household', 'is_appliance', 'next_date'])]
    
    def __str__(self):
        typ = '家電' if self.is_appliance else '設備'
        return f'[{typ}] {self.target_name}'
    
    def _freq_delta(self):
        if self.frequency == '6m':
            return relativedelta(months=+6)
        if self.frequency == '24m':
            return relativedelta(months=+24)
        return relativedelta(months=+12)
    
    def recompute_dates(self):
        self.next_date = self.last_date + self._freq_delta()
        self.task_date = self.next_date - relativedelta(days=30)
    
    def save(self, *args, **kwargs):
        if not self.next_date or not self.task_date:
            self.recompute_dates()
        super().save(*args, **kwargs)
        