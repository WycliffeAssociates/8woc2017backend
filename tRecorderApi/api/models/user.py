from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    icon_hash = models.CharField(max_length=255)
    name_audio = models.CharField(max_length=255)
