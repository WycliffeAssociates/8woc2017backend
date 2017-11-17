from django.db import models
from .chapter import Chapter
#from .comment import Comment
from django.contrib.contenttypes.fields import GenericRelation

class Chunk(models.Model):
    startv = models.IntegerField(default=0)
    endv = models.IntegerField(default=0)
    chapter = models.ForeignKey(
        "Chapter",
        on_delete=models.CASCADE
    )
    comments = GenericRelation("Comment")

    class Meta:
        ordering = ["startv"]

    def __str__(self):
        return '{}:{}-{}'.format(
            Chapter.objects.get(pk=self.chapter).number,
            self.startv,
            self.endv
        )

    @staticmethod
    def create_chunk_filter(data):
        chunk_filter = {}
        if data is not None:
            #return here since it's enough to get all chunks for a chapter
            if "chapter_id" in data:
                chunk_filter["id"] = data["chapter_id"]
                return chunk_filter

            if "project_id" in data:
                chunk_filter["chapter__project__id"] = data["project_id"]
            if "chapter_number" in data:
                chunk_filter["chapter__number"] = data["chapter_number"]
            #This is specific enough to grab chunks of a chapter, so return after
            if "project_id" in data and "chapter_number" in data:
                return chunk_filter

            if "anthology_slug" in data:
                chunk_filter["chapter__project__anthology__slug__iexact"] = data["anthology_slug"]
            if "book_slug" in data:
                chunk_filter["chapter__project__book__slug__iexact"] = data["book_slug"]
            if "version_slug" in data:
                chunk_filter["chapter__project__version__slug__iexact"] = data["version_slug"]
            return chunk_filter

    @staticmethod
    def get_chunks(data):
        chunk_filter = Chunk.create_chunk_filter(data)
        chunks = Chunk.objects.filter(**chunk_filter)
        ls = []
        for chunk in chunks:
            ck = {"endv":chunk.endv, "startv":chunk.startv, "id":chunk.id}
            ls.append(ck)
        return ls