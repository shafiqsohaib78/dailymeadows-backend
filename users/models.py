from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db.models.signals import post_delete, post_init, post_save, pre_save, pre_delete
from articles.utils import unique_username_generator, unique_id_generator
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken

import jwt
expire = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]
# Create your models here.


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email,  name, password, **other_fields)

    def create_user(self, email,  name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email,
                          name=name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class NewUser(AbstractBaseUser, PermissionsMixin):

    unique_id = models.CharField(max_length=20, blank=True, unique=True)
    email = models.EmailField(_('email address'), max_length=50, unique=True)
    name = models.CharField(max_length=30, blank=True)
    username = models.CharField(max_length=30, blank=True, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name',]

    @property
    def token(self):
        refresh = RefreshToken.for_user(self)
        return str(refresh)
        # return str(refresh.access_token)


def user_pre_save_reciever(sender, instance, *args, **kwargs):
    if not instance.unique_id:
        instance.unique_id = unique_id_generator(instance)
    if not instance.username:
        instance.username = unique_username_generator(instance)


pre_save.connect(user_pre_save_reciever, sender=NewUser)


class GeneralUserAppInfo(models.Model):
    ip = models.CharField(max_length=15, blank=False)
    country = models.CharField(max_length=56, blank=False)
    region = models.CharField(max_length=86, blank=False)
    city = models.CharField(max_length=86, blank=False)
    browser = models.CharField(max_length=25, blank=False)
    browser_v = models.CharField(max_length=15, blank=False)
    time = models.TimeField(auto_now_add=True)
    date = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.ip)
