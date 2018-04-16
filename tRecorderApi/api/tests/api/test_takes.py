"""
    This module contains test cases which test the Take objects interactions
    with the API. For more information for how the Take object is defined,
    please read the Take object class definition in models/take.py.
"""
import random
import string
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from ...models import Language, Anthology, Book, Version, Mode, Project, Chapter, Chunk, Take


class TakesApiTest(TestCase):
    """
        This test case contains tests which verify the behavior of the API as it
        interacts with the Take object class.
    """
    def setUp(self):
        self.client = APIClient()
        self.lang = Language.objects.create(
            slug='yo',
            name='yolo')
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
        self.proj = Project.objects.create(
            version=self.version,
            mode=self.mode,
            anthology=self.anthology,
            language=self.lang,
            book=self.book)
        self.chap = Chapter.objects.create(
            number=1,
            checked_level=1,
            published=False,
            project=self.proj)
        self.chunk = Chunk.objects.create(
            startv=0,
            endv=3,
            chapter=self.chap)
        self.take = Take.objects.create(
            location="take1.mp3",
            published=True,
            duration=0,
            markers="{\"test\" : \"true\"}",
            rating=2,
            chunk=self.chunk)
        self.random_url = ''.join(random.choices(
            string.ascii_uppercase + string.digits,
            k=random.randint(1, 15)))

    def test_get_request_returns_ok(self):
        """
            Verify send a GET request to localhost:8000/api/takes/ sends an
            HTTP Response back with a status code of 200.
            Input:    GET request to localhost:8000/api/takes/
            Expected: HTTP response returned with status code 200
        """
        response = self.client.get('/api/takes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_with_id(self):
        """
            Verify an object that has a record inside the DB can be accessed in
            the API using a URL containing its respective id.
            Input:    GET request to 'localhost:8000/api/takes/' with a parameter
                        containing the take object's id appended to it.
            Expected: API will return an HTTP response with status code 200

        """
        response = self.client.get('/api/takes/' + str(self.take.id) + '/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get('/api/takes/?id='+str(self.take.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_null_get_request(self):
        """
            Verify sending a GET request to the API with an id parameter for a
            Take object that does not exist within the DB will return an HTTP
            response with a status code of 404.
            Input:    Get request to localhost:8000/api/takes/1000
            Expected: HTTP response will be returned with status code 404
        """
        response = self.client.get('/api/takes/1000/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_random_parameter_in_url(self):
        """
            Verify sending a GET request for a take object using a parameter in
            the URL that does not exist will return a bad request response
            (HTTP response with status code 400).
            Input:    GET request to 'localhost:8000/api/takes/' with a random string
                        as an additional parameter
            Expected: The API will return with an HTTP response with a status
                        code of 400.
        """
        response = self.client.get('/api/takes/?' + self.random_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_is_updated(self):
        """
            Verify a Take object can be updated using the API.
            Input:    PUT request to API URL that points to the Take object
                        created in the setup method with a change to one of its
                        attributes.
            Expected: The Take object will be updated with its new data.
        """
        self.client.patch('/api/takes/' + str(self.take.id) +'/', {"rating": 1})
        take = Take.objects.get(id=self.take.id)
        self.assertEqual(take.rating, 1)

    # TODO: The test below performs a similar test to the one above. Please review
    # whether this test should be removed due to redundancy.
    # def test_published_is_updated(self):
        # """
            # Verify a Take object can be updated using the API.
            # Input:    PUT request to API URL that points to the Take object
                        # created in the setup method with a change to one of its
                        # attributes.
            # Expected: The Take object will be updated with its new data.
        # """
        # self.client.patch('/api/takes/' + str(self.take.id) + '/', {"published": False})
        # take = Take.objects.get(id=self.take.id)
        # self.assertFalse(take.published)

    def tearDown(self):
        self.lang.delete()
        self.anthology.delete()
        self.book.delete()
        self.version.delete()
        self.mode.delete()
        self.proj.delete()
        self.chap.delete()
        self.chunk.delete()
        self.take.delete()
