from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from .chapter import Chapter
from .chunk import Chunk
from .take import Take


class Comment(models.Model):
    location = models.CharField(max_length=255)
    date_modified = models.DateTimeField(default=now)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ["date_modified"]

    def __str__(self):
        return self.location

    @staticmethod
    def get_comments(chunk_id=None, take_id=None, chapter_id=None):
        commented_object = None
        if chunk_id is not None:
             commented_object = Chunk.objects.get(id=chunk_id)
        elif take_id is not None:
            commented_object = Take.objects.get(id=take_id)
        elif chapter_id is not None:
            commented_object = Chapter.objects.get(id=chapter_id)
        else:
            return None
        comments = commented_object.comments.all()
        return comments
