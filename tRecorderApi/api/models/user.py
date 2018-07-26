from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.hashers import make_password


class User(AbstractUser):
    icon_hash = models.CharField(max_length=255)
    name_audio = models.CharField(max_length=255)
    is_social = models.BooleanField(default=False)

    @staticmethod
    def import_user(user):
        username = str(uuid.uuid1())[:8]
        user_obj, u_created = User.objects.get_or_create(
            icon_hash=user['icon_hash'],
            username=username,
            name_audio=user['location']
        )
        user_obj.password = make_password("P@ssw0rd")
        user_obj.save(update_fields=['password'])
        return user_obj
