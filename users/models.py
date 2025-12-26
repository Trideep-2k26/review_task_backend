from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number, name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required')
        user = self.model(phone_number=phone_number, name=name, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.phone_number})"
