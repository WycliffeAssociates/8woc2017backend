from django.test import TestCase
from ..models import Book, Anthology
from rest_framework.test import APIClient


class IntegrationBookTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.anthology = Anthology.objects.create(
            slug='nt', name="new testament", id=1)
        self.anthology2 = Anthology.objects.create(
            slug='ot', name="old testament", id=2)
        self.Book1 = Book.objects.create(
            name='mark', number=5, slug='mrk', anthology=self.anthology)
        self.Book2 = Book.objects.create(
            name='john', number=1, slug='jhn', anthology=self.anthology)
        self.Book2 = Book.objects.create(
            name='genesis', number=1, slug='gem', anthology=self.anthology2)

    def test_get_book(self):
        book_filter = Book.objects \
            .filter(slug__iexact="mrk", anthology__slug__iexact="nt")
        get_book = Book.get_books(book_filter)
        for book in get_book:
            self.assertIn("id", book)
            self.assertIn("slug", book)
            self.assertIn("name", book)
            self.assertIn("book_num", book)
