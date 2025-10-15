from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Household(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class Member(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('member', 'Member')]
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    avatar_url = models.URLField(blank=True)
    pin_hash = models.CharField(max_length=255, blank=True)
    pin_updated_at = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default='active')

    def __str__(self):
        return f"{self.display_name} ({self.household.name})"
class JoinCode(models.Model):
    code8 = models.CharField(max_length=8, unique=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()
    max_uses = models.PositiveIntegerField(default=10)
    revoked = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def is_valid(self):
        now = timezone.now()
        return (self.revoked is None) and (self.expires_at > now) and (self.max_uses)

    