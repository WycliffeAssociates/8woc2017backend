from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import random
import string

from ...models import Anthology


class AnthologyApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.anthology = Anthology.objects.create(
            name='New Testament',
            slug='ot')
        self.random_url = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=random.randint(1, 15)))

    def test_number_of_items_are_equal(self):
        anthology_num = Anthology.objects.count()
        response = self.client.get('/api/anthologies/')
        self.assertEqual(len(response.data), anthology_num)

    def test_get_request_has_200_status_code(self):
        response = self.client.get('/api/anthologies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_id_has_200_status_code(self):
        response = self.client.get('/api/anthologies/' + str(self.anthology.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/anthologies/?id=' + str(self.anthology.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_non_existent_id_has_404_status_code(self):
        response = self.client.get('/api/anthologies/4/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_random_text_as_parameter_gives_400_status_code(self):
        response = self.client.get('/api/anthologies/?'+self.random_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slug_equals_ot_as_parameter_has_len_one(self):
        response = self.client.get('/api/anthologies/?slug=ot')
        self.assertEqual(len(response.data), 1)
    
    def tearDown(self):
        self.anthology.delete()
