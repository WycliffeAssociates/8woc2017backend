from django.test import TestCase
from api.models import User
from rest_framework.test import APIClient
from rest_framework import status

base_url = 'http://127.0.0.1:8000/api/'
my_file = 'media/dump'

class IntegrationUserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {'name': 'tester', 'agreed': True, 'picture': 'test.pic'}
        self.user_object = User(name='testy', agreed=True, picture='mypic.jpg', id=1)

    def test_that_api_can_create_user_object(self):
        """Test the API has user creation capability:
        Sending JSON User Object To API and
        Expecting HTTP Success Message Returned"""
        self.response = self.client.post(base_url + 'users/', self.user_data, format='json')
        self.assertEquals(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_update_user_object(self):
        """Test that the API can update a User object:
        Sending User Object To API and
        Expecting HTTP Success Message Returned"""
        self.user_object.save()
        response = self.client.put(base_url + 'users/1/', {'name': 'nick', 'picture': 'newpic.jpg'},
                                   format='json')  # picture is required to change when updating user object
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(User.objects.filter(id=1)))

    def test_get_user_request_returns_success(self):
        """Testing API can handle GET requests for User objects"""
        self.user_object.save()
        response = self.client.get(base_url + 'users/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(User.objects.filter(id=1)))  # check that object was deleted from temporary database

    def test_that_api_can_delete_user_objects(self):
        """Testing that the API has User Object deletion functionality"""
        self.user_object.save()
        response = self.client.delete(base_url + 'users/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)  # after deleting an object, nothing should be returned, which is why we check against a 204 status code
        self.user_object.delete()
