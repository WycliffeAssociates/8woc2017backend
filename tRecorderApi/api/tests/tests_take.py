from django.test import TestCase
from api.models import Take, Chapter, Project, Chunk, Book, Language,User,Comment
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings

base_url = 'http://127.0.0.1:8000/api/'
my_file = settings.BASE_DIR + 'media/dump'
location_wav = settings.BASE_DIR + '/en-x-demo2_ulb_b42_mrk_c06_v01-03_t11.wav'


class IntegrationTakeTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lang = Language.objects.create(slug='en-x-demo', name='english')
        self.book = Book.objects.create(name='mark', booknum=5, slug='mrk')
        self.proj = Project.objects.create(version='ulb', mode='chunk',
                                      anthology='nt', is_source=False, language=self.lang,
                                      book=self.book)
        self.chap = Chapter.objects.create(number=1, checked_level=1, is_publish=False, project=self.proj)
        self.chunk = Chunk.objects.create(startv=0, endv=3, chapter=self.chap)
        self.user = User.objects.create(name='testy', agreed=True, picture='mypic.jpg')
        self.take = Take.objects.create(location=location_wav, is_publish=True,
                                   duration=0, markers="{\"test\" : \"true\"}", rating=2, chunk=self.chunk, user=self.user)
        self.take_data = {
            "id": 22,
            "location": "my_file",
            "duration": 3,
            "rating": 3,
            "is_publish": True,
            "markers": "marked",
            "date_modified": "2017-07-26T12:29:02.828000Z"}

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
        self.response = self.client.put(base_url + 'takes/1/', {"duration": 1}, format='json')
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.assertEqual(0, len(Take.objects.filter(duration=1)))

    def test_get_take_request_returns_success(self):
        """Testing API can handle GET requests for Take objects"""
        response = self.client.get(base_url + 'takes/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_that_api_can_delete_take_objects(self):
        """Testing that the API has Take Object deletion functionality"""
        self.response = self.client.delete(base_url + 'takes/1/')
        self.assertEqual(self.response.status_code,
                         status.HTTP_200_OK)   # check that take_object was deleted from temporary database
        self.assertEqual(0,
                         len(Take.objects.filter(id=1)))


    def tearDown(self):
        self.take.delete()
        self.user.delete()
        self.chunk.delete()
        self.chap.delete()
        self.proj.delete()
        self.book.delete()
        self.lang.delete()
