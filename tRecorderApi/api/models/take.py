from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.timezone import now


# from .comment import Comment

class Take(models.Model):
    location = models.CharField(max_length=255)
    duration = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    published = models.BooleanField(default=False)
    markers = models.TextField(blank=True)
    date_modified = models.DateTimeField(default=now)
    chunk = models.ForeignKey("Chunk", on_delete=models.CASCADE)
    comment = GenericRelation("Comment")

    class Meta:
        ordering = ["chunk"]

    def __str__(self):
        return '{} ({})'.format(self.chunk, self.id)

    def get_takes(chunk_id):
        takes = Take.objects.filter(id=chunk_id)
        ls = []
        for take in takes:
            tk = {
                "rating": take.rating,
                "published": take.published,
                "markers": take.markers,
                "location": take.location,
                "duration": take.duration,
                "id": take.id
            }
            ls.append(tk)
        return ls

    @staticmethod
    def by_project_id(id):
        return Take.objects.filter(chunk__chapter__project=id)
