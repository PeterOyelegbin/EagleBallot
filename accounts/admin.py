from django.contrib import admin
from .models import UserModel

# Register your models here.
@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "state_of_resident")
    list_filter = ("state_of_resident",)
