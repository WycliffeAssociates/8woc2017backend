from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from .chapter import Chapter


class Chunk(models.Model):
    startv = models.IntegerField(default=0)
    endv = models.IntegerField(default=0)
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    comments = GenericRelation("Comment")

    class Meta:
        ordering = ["startv"]

    def __str__(self):
        return "{}"

    @property
    def has_comment(self):
        return Chunk.objects.filter(comments__object_id=self.id).exists()

    @property
    def published_take(self):
        return self.takes.filter(published=True).first()

    @staticmethod
    def import_chunk(chapter, startv, endv):
        chunk_obj, ck_created = Chunk.objects.get_or_create(
            chapter=chapter,
            startv=startv,
            endv=endv,
            defaults={
                'startv': startv,
                'endv': endv,
                'chapter': chapter

            }
        )
        return chunk_obj
