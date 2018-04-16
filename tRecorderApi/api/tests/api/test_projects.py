from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import random
import string

from ...models import Language, Anthology, Book, Version, Mode, Project


class ProjectsApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.lang = Language.objects.create(
            slug='en-x-demo',
            name='english')
        self.anthology = Anthology.objects.create(
            slug='ot',
            name="old testament")
        self.book = Book.objects.create(
            name='mark',
            number=5,
            slug='mrk',
            anthology=self.anthology)
        self.version = Version.objects.create(
            slug='ulb',
            name="Unlocked literal bible")
        self.mode = Mode.objects.create(
            slug="chk",
            name="chunk",
            unit=1)
        self.project = Project.objects.create(
            version=self.version,
            mode=self.mode,
            anthology=self.anthology,
            language=self.lang,
            book=self.book)
        self.random_url = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=random.randint(1, 15)))

    def test_number_of_items_are_equal(self):
        language_num = Project.objects.count()
        response = self.client.get('/api/projects/')
        self.assertEqual(len(response.data), language_num)

    def test_get_request_has_200_status_code(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_id_has_200_status_code(self):
        response = self.client.get('/api/projects/' + str(self.project.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/projects/?id=' + str(self.project.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_non_existent_id_has_404_status_code(self):
        response = self.client.get('/api/projects/4/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_random_text_as_parameter_gives_400_status_code(self):
        response = self.client.get('/api/projects/?'+self.random_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        self.lang.delete()
        self.anthology.delete()
        self.book.delete()
        self.version.delete()
        self.mode.delete()
        self.project.delete()
