import hashlib
import os

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.timezone import now

from api.models import book, language, chunk, anthology, version, chapter, mode

Language = language.Language
Book = book.Book
Chunk = chunk.Chunk
Anthology = anthology.Anthology
Version = version.Version
Chapter = chapter.Chapter
Mode = mode.Mode


class Take(models.Model):
    location = models.CharField(max_length=255)
    duration = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    published = models.BooleanField(default=False)
    markers = models.TextField(blank=True)
    date_modified = models.DateTimeField(default=now)
    chunk = models.ForeignKey("Chunk", on_delete=models.CASCADE, related_name='takes')
    comments = GenericRelation("Comment")

    class Meta:
        ordering = ["chunk", "date_modified"]

    def __str__(self):
        return '{} ({})'.format(self.chunk, self.id)

    @property
    def take_num(self):
        return self.location[len(self.location) - 6:len(self.location) - 4:1]

    @property
    def name(self):
        return self.location.split(os.sep)[-1:][0]

    @property
    def md5hash(self):
        hash_md5 = hashlib.md5()
        try:
            with open(self.location, "rb") as file:
                for chunk in iter(lambda: file.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""

    @staticmethod
    def import_takes(file_path, duration, markers, rating, chunk):
        take = Take(location=file_path,
                    chunk=chunk,
                    duration=duration,
                    rating=rating,
                    markers=markers,
                    )
        take.save()
