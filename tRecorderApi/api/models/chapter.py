from django.db import models


class Chapter(models.Model):
    number = models.IntegerField(default=0)
    checked_level = models.IntegerField(default=0)
    published = models.BooleanField(default=False)
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return '{}'.format(self.number)
