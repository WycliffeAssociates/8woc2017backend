from unittest import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from api.models import Language

base_url = 'http://localhost:8000/api/'

class TestLanguageView(TestCase):

    def setUp(self):

        self.client = APIClient()

        # Need to setup test database

        self.language= Language(slug='en', name='english')
        self.language.save()

    def test_get_langs_without_slug_returns_success(self):
        response = self.client.get(base_url + 'get_langs/',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_langs_with_slug_returns_success(self):
        response = self.client.post(base_url + 'get_langs/',{"slug":"en"},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_langs_with_slug_returns_204(self):
        response = self.client.post(base_url + 'get_langs/',{"slug":"npp"},format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        self.language.delete()