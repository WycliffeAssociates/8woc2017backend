from django.db import models


class Mode(models.Model):
    SINGLE = 0
    MULTI = 1

    slug = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    unit = models.IntegerField(default=SINGLE)

    class Meta:
        unique_together = ('slug', 'unit',)

    def __str__(self):
        return self.name

    @staticmethod
    def import_mode(mode):
        # Create mode in database if it does not exist
        mode["type"] = 1 if mode["type"] == "MULTI" else 0

        mode_obj, m_created = Mode.objects.get_or_create(
            name=mode['name'],
            slug=mode['slug'],
            unit=mode['type'],
            defaults={
                'slug': mode["slug"],
                'name': mode["name"],
                'unit': mode["type"]
            }
        )
        return mode_obj
