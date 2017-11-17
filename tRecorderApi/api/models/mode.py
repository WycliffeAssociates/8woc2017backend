from django.db import models


class Mode(models.Model):
    SINGLE = 0
    MULTI = 1

    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255)
    unit = models.IntegerField(default=SINGLE)

    def __str__(self):
        return self.name