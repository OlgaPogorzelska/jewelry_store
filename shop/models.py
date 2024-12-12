import uuid

from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class CustomerUser(AbstractUser, PermissionsMixin):
    """
        Custom user model for a jewelry store.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=9, unique=True, null=True)
    street = models.CharField(max_length=255, null=True)
    house_number = models.CharField(max_length=10, null=True)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    city = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=6, null=True)
    country = models.CharField(max_length=100, null=True, default="Poland")

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = ["username"]

    is_staff = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = str(uuid.uuid4())[:30]  # Generuje unikalne ID
        super().save(*args, **kwargs)

    @property
    def full_street(self):
        if self.apartment_number:
            return (f"{self.street}  {self.house_number} "
                    f"{self.apartment_number}")
        return f"{self.street}  {self.house_number}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
