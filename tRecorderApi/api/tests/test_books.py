"""
    This module contains test cases that test the Book model independently from
    the api. APIClient library still needed to generate Book model data inside
    of database.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from ..models import Book, Anthology
from ..serializers import BookSerializer


class BookModelTestCases(TestCase):
    """
        Test cases which verify the behavior of the Book class as defined in the
        api/models/book.py file.
    """
    def setUp(self):
        self.client = APIClient()
        self.anthology = Anthology.objects.create(
            slug='nt',
            name="new testament",
            id=1)
        self.book = Book.objects.create(
            name='mark',
            number=5,
            slug='mrk',
            anthology=self.anthology)
        self.book_serializer = BookSerializer(instance=self.book)

    def test_serializer_ouput(self):
        """
            Verify the BookSerializer class outputs data containing
            the keys defined in the BookSerializer class and the Book class.
            For more information about the classes, see api/serializers.py and
            api/models/books.py.
            Input: data = serialized data of book object created in setup
            Expected: data will contain all of the keys listed above
        """
        data = self.book_serializer.data
        self.assertIn("id", data)
        self.assertIn("slug", data)
        self.assertIn("name", data)
        self.assertIn("number", data)

    # def test_get_book(self):
        # book_filter = Book.objects \
            # .filter(slug__iexact="mrk", anthology__slug__iexact="nt")
        # get_book = Book.get_books(book_filter)
        # for book in get_book:
            # self.assertIn("id", book)
            # self.assertIn("slug", book)
            # self.assertIn("name", book)
            # self.assertIn("book_num", book)

    def tearDown(self):
        self.anthology.delete()
        self.book.delete()
