from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser precisa precisa estar como True')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff precisa precisa estar como True')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Esse modelo representa um usuário que seja estudante ou um instrutor de um curso.
    """

    email = models.EmailField(_('E-mail'), unique=True)
    name = models.CharField(_('Name'), max_length=150)
    username = models.CharField(_('Username'), max_length=150)
    job_title = models.CharField(max_length=255, null=True)
    locale = models.CharField(max_length=255, null=True)
    bio = models.TextField(null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'username']

    def __str__(self):
        return f'User({self.username})'
