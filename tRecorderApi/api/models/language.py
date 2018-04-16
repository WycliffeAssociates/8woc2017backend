from django.db import models


class Language(models.Model):
    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


    @staticmethod
    def import_language(language):
        # Create Language in database if it's not there
        language_obj, l_created = Language.objects.get_or_create(
            slug=language["slug"],
            defaults={
                'slug': language["slug"],
                'name': language["name"]
            }
        )
        return language_obj
