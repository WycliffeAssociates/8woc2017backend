from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import random
import string

from ...models import Mode


class ModesApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.mode = Mode.objects.create(
            slug="chk",
            name="chunk",
            unit=1)
        self.random_url = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=random.randint(1, 15)))

    def test_number_of_items_are_equal(self):
        language_num = Mode.objects.count()
        response = self.client.get('/api/modes/')
        self.assertEqual(len(response.data), language_num)

    def test_get_request_has_200_status_code(self):
        response = self.client.get('/api/modes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_id_has_200_status_code(self):
        response = self.client.get('/api/modes/' + str(self.mode.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/modes/?id=' + str(self.mode.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_non_existent_id_has_404_status_code(self):
        response = self.client.get('/api/modes/4/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_random_text_as_parameter_gives_400_status_code(self):
        response = self.client.get('/api/modes/?'+self.random_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_slug_equals_en_x_demo_as_parameter_has_len_one(self):
        response = self.client.get('/api/modes/?slug=chk')
        self.assertEqual(len(response.data), 1)

    def tearDown(self):
        self.mode.delete()
