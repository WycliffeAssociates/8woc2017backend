from django.test import TestCase
from api.models import Language
from rest_framework.test import APIClient
from rest_framework import status

base_url = 'http://127.0.0.1:8000/api/'
my_file = 'media/dump'


class IntegrationLanguageTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lang_data = {'lang': 'english', 'code': 'abc'}
        self.language_object = Language(slug='en-x-demo', name='english', id=1)

    def test_api_can_create_lang_object(self):
        """Test the API has lang creation capability:
        Sending JSON Lang Object To API and
        Expecting HTTP Success Message Returned"""
        self.response = self.client.post(base_url + 'languages/', self.lang_data, format='json')  # send POST to API
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_update_language_object(self):
        """Test that the API can update a language object:
        Sending Language Object To API and
        Expecting HTTP Success Message Returned"""
        self.language_object.save()
        response = self.client.put(base_url + 'languages/1/', {'code': 'ex-demo'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.language_object.delete()
        self.assertEqual(0, len(Language.objects.filter(id=1)))

    def test_get_language_request_returns_success(self):
        """Testing API can handle GET requests for Language objects"""
        self.language_object.save()
        response = self.client.get(base_url + 'languages/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.language_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(Language.objects.filter(id=1)))  # check that object was deleted from temporary database

    def test_that_api_can_delete_language_objects(self):
        """Testing that the API has Language Object deletion functionality"""
        self.language_object.save()
        response = self.client.delete(base_url + 'languages/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_204_NO_CONTENT)  # after deleting an object, nothing should be returned, which is why we check against a 204 status code
        self.language_object.delete()
