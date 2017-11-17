from django.db import models

class Book(models.Model):
    anthology = models.ForeignKey("Anthology", on_delete=models.CASCADE)
    slug = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    number = models.IntegerField(default=0)

    @staticmethod
    def get_books(books):
        book_list = []
        dic = {}
        for book in books:
            dic = {
                "id": book.id,
                "slug": book.slug,
                "name": book.name,
                "book_num": book.number
            }
            book_list.append(dic)
        return book_list

    class Meta:
        ordering = ["number"]
        unique_together = ("anthology", "slug")

    def __str__(self):
        return self.name
