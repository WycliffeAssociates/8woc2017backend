import os
import json
import re

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


class Chapter(models.Model):
    number = models.IntegerField(default=0)
    checked_level = models.IntegerField(default=0)
    published = models.BooleanField(default=False)
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="chapters"
    )
    comments = GenericRelation("Comment", related_query_name="comments")

    class Meta:
        ordering = ["number"]

    def __str__(self):
        return '{}'.format(self.number)

    @property
    def date_modified(self):
        # take = Take.objects.filter(project=self.project) \
        #     .order_by('date_modified') \
        #     .first()
        # if take is not None:
        #     return take.date_modified
        # else:
        return 0

    @property
    def contributors(self):
        return ""

    @property
    def has_comment(self):
        return Chapter.objects.filter(comments__object_id=self.id).exists()

    @property
    def has_takes(self):
        takes_count = 0
        for chunk in self.chunks.all():
            takes_count += chunk.takes.count()

        return takes_count > 0

    @property
    def completed(self):
        chunks_done = self.get_uploaded_chunks()
        total_chunks = self.get_total_chunks(self.project.book.slug, self.number)
        try:
            return int(round((chunks_done / total_chunks) * 100))
        except ZeroDivisionError:
            return 0

    @property
    def total_chunks(self):
        return self.get_total_chunks(self.project.book.slug, self.number)

    @property
    def uploaded_chunks(self):
        return self.get_uploaded_chunks()

    @property
    def published_chunks(self):
        count = 0
        for chunk in self.chunks.all():
            if chunk.published_take is not None:
                count += 1
        return count

    def get_uploaded_chunks(self):
        return self.chunks.count()

    def get_total_chunks(self, book_name_slug, chapter_number):
        length = 0
        lastvs = 0
        # TODO 'os' will not be useful when the code migrates to AWS
        for dirpath, dirnames, files in os.walk(os.path.abspath('static/chunks/')):
            if dirpath[-3:] == book_name_slug:
                for fname in os.listdir(dirpath):
                    f = open(os.path.join(dirpath, fname), "r")
                    sus = json.loads(f.read())

                    for ch in sus:
                        n = re.sub(r'([0-9]{2,3})-([0-9]{2,3})', r'\1', ch["id"])

                        if int(n) == chapter_number:
                            lastvs = ch["lastvs"]
                            length += 1
                break

        if str(self.project.mode) == "verse":
            return int(lastvs)
        return length

    @staticmethod
    def import_chapter(project, number, checked_level):
        # Create Chapter in database if it's not there
        chapter_obj, cr_created = Chapter.objects.get_or_create(
            project=project,
            number=number,
            defaults={
                'number': number,
                'checked_level': checked_level,
                'project': project
            }
        )

        return chapter_obj
