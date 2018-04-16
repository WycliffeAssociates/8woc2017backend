from django.db import models


class Book(models.Model):
    anthology = models.ForeignKey("Anthology", on_delete=models.CASCADE)
    slug = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    number = models.IntegerField(default=0)

    class Meta:
        ordering = ["number"]
        unique_together = ("anthology", "slug")

    def __str__(self):
        return self.name

    @staticmethod
    def import_book(book, anthology):
        # Create Book in database if it's not there
        book_obj, b_created = Book.objects.get_or_create(
            slug=book["slug"],
            defaults={
                'slug': book['slug'],
                'number': book['number'],
                'name': book['name'],
                'anthology': anthology
            }
        )
        return book_obj
