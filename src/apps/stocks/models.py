from datetime import datetime, timedelta, time
from django.db import models
from django.utils import timezone

from apps.user.models import Household, Users
from apps.shopping.models import ShoppingItem

class StockItem(models.Model):
    CATEGORY_CHOICES = [
        ('daily', '日用品'),
        ('hygiene', '衛生用品'),
        ('kitchen', 'キッチン用品'),
        ('cleaning', '掃除用品'),
        ('laundry', '洗濯用品'),
    ]
    PERIOD_CHOICES = [(d, f'{d}日') for d in (10, 20, 30, 40, 50, 60)]

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='stocks')
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES)
    stock_name = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField(default=1)
    period_days = models.PositiveIntegerField(choices=PERIOD_CHOICES)
    purchase_date = models.DateField()
    remind_at = models.DateTimeField(null=True, blank=True)
    open_shopping_item = models.ForeignKey(ShoppingItem, null=True, blank=True, on_delete=models.SET_NULL, related_name='from_stock')
    enqueued_to_shopping = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'[{self.get_category_display()}] {self.stock_name}'
    
    @property
    def is_due(self):
        return (self.remind_at and self.remind_at <= timezone.now() and not self.enqueued_to_shopping)
    
    def calc_remind_at(self) -> datetime:
        base = datetime.combine(self.purchase_date, time(hour=9))
        return timezone.make_aware(base) + timedelta(days=int(self.period_days) - 2)
    
    def save(self, *args, **kwargs):
        if not self.remind_at:
            self.remind_at = self.calc_remind_at()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'[{self.get_category_display()}] {self.stock_name}'
