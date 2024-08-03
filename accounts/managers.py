from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import requests, random, string


base_url = "https://api.sandbox.youverify.co/"
headers = {
    # "Authorization": f"Bearer {settings.YOUVERIFY_KEY}",
    "Token": f"{settings.YOUVERIFY_KEY}",
    "Content-Type": "application/json",
}

# user ID verification function
def verify_id(user_id):
    url = base_url + "v2/api/identity/ng/nin"
    data = {
        "id": user_id,
        "isSubjectConsent": True,
    }
    response = requests.post(url, headers=headers, json=data)
    return response


# otp generation function
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))


"""
Custom user model manager where email is the unique identifiers
for authentication instead of username.
"""
class UserModelManager(BaseUserManager):
    # Create and save a user with the given email and password.
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("User must have an email address"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Create and save a SuperUser with the given email and password.
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


# Asynchronous email sending
def send_async_email(subject, message, from_email, recipient_list):
    try:
        email = EmailMultiAlternatives(subject, message, from_email, recipient_list)
        email.send()
    except Exception as e:
        print(f"Error sending email: {e}")
