from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    icon_hash = models.CharField(max_length=255)
    name_audio = models.CharField(max_length=255)
    is_social = models.BooleanField(default=False)

    @staticmethod
    def import_user(user):
        username = user['name_audio'][:-4]
        user_obj, u_created = User.objects.get_or_create(
            icon_hash=user['icon_hash'],
            username=username,
            name_audio=user['location']
        )
        return user_obj
