
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from user.models_manager import UserManager
from user.model_choices import FRIEND_REQUEST_CHOICES

class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, auto_now_add=True)
    updated_at = models.DateTimeField(db_index=True, auto_now=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)

class User(AbstractBaseUser, BaseModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class UserData(BaseModel):
    user = models.OneToOneField(User, related_name='user_data', on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=155)

    def __str__(self):
        return f'{self.user} - {self.name}'
    
class FriendRequest(BaseModel):
    from_user = models.ForeignKey(UserData, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(UserData, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=FRIEND_REQUEST_CHOICES, default="pending")

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user} -> {self.to_user} ({self.status})'