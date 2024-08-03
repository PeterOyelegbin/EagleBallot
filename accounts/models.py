from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from uuid import uuid4
from .managers import UserModelManager


# Create your models here.
class UserModel(AbstractUser):
    """
    This model will serve as the default authentication model via AUTH_USER_MODEL in settings.py
    """
    username = None
    id = models.UUIDField(default=uuid4, unique=True, primary_key=True, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    voters_id = models.CharField(max_length=25, unique=True)
    state_of_resident = models.CharField(max_length=25)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["voters_id"]

    objects = UserModelManager()

    def __str__(self):
        return f"{self.id} {self.email}"

    class Meta:
        ordering = ['-date_joined']


class OtpToken(models.Model):
    """
    This model will serve as the token authentication model for AUTH_USER_MODEL
    """
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=10)
