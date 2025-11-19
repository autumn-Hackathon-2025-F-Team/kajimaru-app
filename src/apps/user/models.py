from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Household(models.Model):
    name = models.CharField(max_length=100)      # UIには出さない（自動生成でOK）
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Users(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('member', 'Member')]
    REL_CHOICES = [('self', 'Self'), ('spouse', 'Spouse'), ('parent', 'Parent'), ('child', 'Child'), ('other', 'Other')]
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, blank=True, default='')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    avatar_key = models.CharField(max_length=50, blank=True, default='')
    pin_hash = models.CharField(max_length=255, blank=True)
    pin_updated_at = models.DateTimeField(null=True, blank=True)
    failed_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default='active')
    relation_to_admin = models.CharField(max_length=10, choices=REL_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def is_locked(self) -> bool:
        return self.locked_until is not None and self.locked_until > timezone.now()
    def __str__(self):
        return self.display_name
    
class JoinCode(models.Model):
    code8 = models.CharField(max_length=8, unique=True, db_index=True)
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    expires_at = models.DateTimeField()            # 発行から５分後
    max_uses = models.PositiveIntegerField(default=10)  # 使われた瞬間
    used_at = models.DateTimeField(null=True, blank=True)      
    revoked = models.BooleanField(default=False)   #手動失効
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def is_valid(self):
        now = timezone.now()
        if self.revoked:
            return False
        if self.expires_at <= now:
            return False
        if self.max_uses and self.max_uses > 0:
            return True
        return True
 
    