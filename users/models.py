import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.MANAGER)
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Пользователь'
        MANAGER = 'manager', 'Менеджер'

    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER, verbose_name='Роль')
    email_verified = models.BooleanField(default=False, verbose_name='Email подтверждён')
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER or self.is_superuser

    def __str__(self):
        return self.email