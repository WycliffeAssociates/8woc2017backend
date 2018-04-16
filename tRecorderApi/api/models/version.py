from django.db import models


class Version(models.Model):
    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    @staticmethod
    def slug_by_version_id(id):
        version = Version.objects.filter(id=id).values('slug')[0]
        return version['slug']

    @staticmethod
    def import_version(version):
        # Create version in database if it does not exist
        version_obj, v_created = Version.objects.get_or_create(
            slug=version["slug"],
            defaults={
                'slug': version["slug"],
                'name': version["name"]

            }
        )
        return version_obj
