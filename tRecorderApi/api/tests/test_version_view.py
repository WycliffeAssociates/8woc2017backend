from unittest import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from api.models import Version

base_url = 'http://localhost:8000/api/'

class TestVersionView(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Need to setup test database

        self.version= Version(slug='ulb', name='Unclocked Literal Bible')
        self.version.save()

    def test_get_version_without_slug_returns_success(self):
        response = self.client.get(base_url + 'get_versions/',format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_version_with_slug_returns_success(self):
        response = self.client.post(base_url + 'get_versions/',{"slug":"ulb"},format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_version_with_slug_returns_204(self):
        response = self.client.post(base_url + 'get_versions/',{"slug":"ulbb"},format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        self.version.delete()