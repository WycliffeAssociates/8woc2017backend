from django.test import TestCase
from api.models import Book
from rest_framework.test import APIClient
from rest_framework import status

base_url = 'http://127.0.0.1:8000/api/'
my_file = 'media/dump'


class IntegrationBookTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.book_data = {'code': 'ex', 'name': 'english', 'booknum': 5}
        self.book_object = Book(name='english', booknum=5, id=1)

    def test_api_can_create_book_object(self):
        """Test the API has book creation capability:
        Sending JSON Book Object To API and
        Expecting HTTP Success Message Returned"""
        self.response = self.client.post(base_url + 'books/', self.book_data, format='json')  # send POST to API
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_update_book_object(self):
        """Test that the API can update a book object:
        Sending Book Object To API and
        Expecting HTTP Success Message Returned"""
        self.book_object.save()
        response = self.client.put(base_url + 'books/1/', {'name': 'spanish'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(Book.objects.filter(id=1)))

    def test_get_book_request_returns_success(self):
        """Testing API can handle GET requests for Book objects"""
        self.book_object.save()
        response = self.client.get(base_url + 'books/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(Book.objects.filter(id=1)))  # check that object was deleted from temporary database

    def test_that_api_can_delete_book_objects(self):
        """Testing that the API has Take Object deletion functionality"""
        self.book_object.save()
        response = self.client.delete(base_url + 'books/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)  # after deleting an object, nothing should be returned, which is why we check against a 204 status code
        self.book_object.delete()