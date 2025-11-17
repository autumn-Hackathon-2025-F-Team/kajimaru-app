from django.db import models
from django.utils import timezone
from apps.user.models import Household, Users

class ShoppingItem(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, db_index=True)
    added_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='shopping_added')
    purchased_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='shopping_bought')
    item_name = models.CharField(max_length=20)
    quantity = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True)
    is_purchased = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    purchased_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['household', 'is_purchased', 'created_at'])]
        constraints = [
            models.UniqueConstraint(
                fields=['household', 'item_name', 'is_purchased'],
                name='uniq_active_item_per_household',
                condition=models.Q(is_purchased=False),
            ),
        ]
    def __str__(self):
        return f'{self.item_name} x{self.quantity}'
    
