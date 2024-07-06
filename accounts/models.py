from django.db import models
from django.contrib.auth.models import AbstractUser
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

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["voters_id"]

    objects = UserModelManager()

    def __str__(self):
        return f"{self.id} {self.email}"

    class Meta:
        ordering = ['-date_joined']
