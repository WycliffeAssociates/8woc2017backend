from django.db import models


class Anthology(models.Model):
    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @staticmethod
    def import_anthology(import_anthology):
        anthology_obj, a_created = Anthology.objects.get_or_create(
            slug=import_anthology["slug"],
            defaults={
                'slug': import_anthology["slug"],
                'name': import_anthology["name"]
            }
        )
        return anthology_obj
