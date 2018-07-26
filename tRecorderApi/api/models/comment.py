from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

from .chapter import Chapter
from .chunk import Chunk
from .take import Take
from .user import User


class Comment(models.Model):
    location = models.CharField(max_length=255)
    date_modified = models.DateTimeField(default=now)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["date_modified"]

    def __str__(self):
        return self.location

    @staticmethod
    def get_comments(chunk_id=None, take_id=None, chapter_id=None):
        commented_object = None
        object_id = None
        if chunk_id is not None:
            commented_object = Chunk
            object_id = chunk_id
        elif take_id is not None:
            commented_object = Take
            object_id = take_id
        elif chapter_id is not None:
            commented_object = Chapter
            object_id = chapter_id
        else:
            return None
        comments = Comment.objects.filter(object_id=object_id,
                                          content_type=ContentType.objects.get_for_model(commented_object))
        return comments

    @staticmethod
    def get_comments_for_take_by_chunk_id(chunk_id):
        takes = Take.objects.filter(chunk=chunk_id)
        take_comment_list = []
        for take in takes:
            comment = Comment.objects.filter(object_id=take.id, content_type=ContentType.objects.get_for_model(Take))
            if comment:
                for cmt in comment:
                    take_comment_list.append(cmt)
        return take_comment_list

    @staticmethod
    def import_comment(comment, comment_type, object_id, user):
        # Create Comment in database if it's not there
        if comment_type == 'chapter':
            q_obj = Chapter.objects.get(pk=object_id)
        elif comment_type == 'chunk':
            q_obj = Chunk.objects.get(pk=object_id)
        elif comment_type == 'take':
            q_obj = Take.objects.get(pk=object_id)
        Comment.objects.get_or_create(
            defaults={
                'content_object': q_obj
            },
            location=comment["location"],
            owner=user
        )
