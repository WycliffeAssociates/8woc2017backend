from django.test import TestCase
from api.models import Take
from rest_framework.test import APIClient
from rest_framework import status

base_url = 'http://127.0.0.1:8000/api/'
my_file = 'media/dump'

class IntegrationTakeTestCases(TestCase):
    def setUp(self):
        """Set up environment for api view test suite"""
        self.client = APIClient()
        self.take_data = {'location': 'test_location', 'chapter': 5, 'is_export': True, 'is_source': False}
        self.take_object = Take(location='test_location', chapter=5, is_export=True, is_source=False, id=1,
                                language_id=1, book_id=1, user_id=1)

    def test_api_can_create_take_object(self):
        """Test the API has take creation capability:
        Sending JSON Take Object To API and
        Expecting HTTP Success Message Returned"""
        self.response = self.client.post(base_url + 'takes/', self.take_data, format='json')  # send POST to API
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_update_take_object(self):
        """Test that the API can update a take object:
        Sending Take Object To API and
        Expecting HTTP Success Message Returned"""
        self.take_object.save()
        response = self.client.put(base_url + 'takes/1/', {'location': 'new_location'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.take_object.delete()
        self.assertEqual(0, len(Take.objects.filter(id=1)))

    def test_get_take_request_returns_success(self):
        """Testing API can handle GET requests for Take objects"""
        self.take_object.save()
        response = self.client.get(base_url + 'takes/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.take_object.delete()  # delete object from temporary database
        self.assertEqual(0,
                         len(Take.objects.filter(id=1)))  # check that take_object was deleted from temporary database

    def test_that_api_can_delete_take_objects(self):
        """Testing that the API has Take Object deletion functionality"""
        self.take_object.save()
        response = self.client.delete(base_url + 'takes/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)  # after deleting an object, nothing should be returned, which is why we check against a 204 status code
        self.take_object.delete()
