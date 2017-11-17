from django.db import models

class Version(models.Model):
    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name