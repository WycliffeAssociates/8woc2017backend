"""
    This module contains test cases for verifying the behavior of the api as it
    interacts with the Book class.
"""
import random
import string
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ...models import Anthology, Book

class BookApiTestCases(TestCase):
    """
        This class defines the test cases which verify the behavior of the api
        as it interacts with the Book class. More information about the Book
        class can be found in the models/book.py file. More information about
        the api and its interaction with the Book class can be found in
        views/book.py file.
    """
    def setUp(self):
        self.client = APIClient()
        self.anthology = Anthology.objects.create(
            slug='ot',
            name="old testament")
        self.book = Book.objects.create(
            name='mark',
            number=5,
            slug='mrk',
            anthology=self.anthology)
        self.random_url = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=random.randint(1, 15)))

    def test_language_dependency(self):
        """
            Verify each book created in the database, creates a language object
            as well.
            Input:    language_num = number of Book objects which exist within the
                                     test database.
            Expected: The number of language objects inside the test database
                      equals language_num
        """
        language_num = Book.objects.count()
        response = self.client.get('/api/books/')
        self.assertEqual(len(response.data), language_num)

    def test_get_request_returns_ok(self):
        """
            Verify making a GET request to the api URL for the books returns an
            HTTPResponse with a status code of 200.
            Input:    GET request to localhost:8000/api/books/
            Expected: HTTP status code 200
        """
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_get_request_with_id_has_200_status_code(self):
        # response = self.client.get('/api/books/1/')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_id_returns_ok(self):
        """
            Verify making a GET request to the api URL for the books that
            specifies an id returns an HTTPResponse with a status code of 200.
            Input:    GET request to localhost:8000/api/books/?id=1
            Expected: api returns a response with status code 200
        """
        response = self.client.get('/api/books/?id=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_null_url_returns_404(self):
        """
            Verify that sending a GET request to the api url for books using an id
            that does not exist within the test database will return an HTTP
            response with a status code of 404.
            Input:    GET request to localhost:8000/api/books/4
            Expected: api returns a response with status code 404
        """
        response = self.client.get('/api/books/1000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_random_url_returns_400(self):
        """
            Verify sending a GET request to the api URL for books with a
            parameter containing a random string will return an HTTP response
            with a status code of 400.
            Input:   self.random_url = random URL pointing to
                                     'localhost:8000/api/books/?' + a random string
            Expected:api returns a response with status code 400.
        """
        response = self.client.get('/api/books/?'+self.random_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_response_length(self):
        """
            Verify api returns the expected number of books given a GET request
            containing a URL with a query set.
            Input:    GET request to localhost:8000/api/books/?slug=mrk
            Expected: api will return a response containing one book object
        """
        response = self.client.get('/api/books/?slug=mrk')
        self.assertEqual(len(response.data), 1)

    def tearDown(self):
        self.anthology.delete()
        self.book.delete()
