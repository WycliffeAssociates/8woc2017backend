from unittest import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from api.models import Anthology

base_url = 'http://localhost:8000/api/'


class TestAnthologyView(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Need to setup test database

        self.anthology = Anthology(slug='old', name='Old Testament')
        self.anthology.save()

    def test_get_anthology_without_slug_returns_success(self):
        response = self.client.get(base_url + 'get_anthologies/',
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_anthology_with_slug_returns_success(self):
        response = self.client.post(
            base_url + 'get_anthologies/', {"slug": "old"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_anthology_with_slug_returns_204(self):
        response = self.client.post(
            base_url + 'get_anthologies/', {"slug": "oldd"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def tearDown(self):
        self.anthology.delete()
