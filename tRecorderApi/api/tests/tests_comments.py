from django.test import TestCase
from api.models import Comment, Project, Take, Book, Language, Chunk, Chapter, Version, Mode, Anthology
from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings

base_url = 'http://127.0.0.1:8000/api/'
my_file = settings.BASE_DIR + 'media/dump'


class IntegrationCommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.language_object = Language.objects.create(
            slug='en-x-demo', name='english')
        self.anthology_object = Anthology.objects.create(
            name="Old Testament", slug="ot")
        self.book_object = Book.objects.create(
            name='Genesis', number=1, slug='gen', anthology=self.anthology_object)
        self.version_object = Version.objects.create(
            name="Unlocked Literal Bible", slug="ulb")
        self.mode_object = Mode.objects.create(
            name="chunk", slug="chunk", unit=Mode.MULTI)
        self.project_object = Project.objects.create(
            version=self.version_object,
            mode=self.mode_object,
            anthology=self.anthology_object,
            published=False,
            language=self.language_object,
            source_language=None,
            book=self.book_object
        )
        self.chapter_object = Chapter.objects.create(
            number=1, checked_level=1, published=False, project=self.project_object)
        self.chunk_object = Chunk.objects.create(
            startv=0, endv=3, chapter=self.chapter_object)
        self.take_object = Take.objects.create(
            location=my_file, published=False, markers="", rating=2, chunk=self.chunk_object)
        self.comment_object = Comment.objects.create(location='test-location',
                                                     object_id=1,
                                                     content_type_id=10
                                                     )
        self.comment_data = {'object': self.take_object.id,
                             'type': 'take', 'comment': "3"}

    def test_api_can_update_comment_object(self):
        """Test that the API can update a User object:
        Sending User Object To API and
        Expecting HTTP Success Message Returned"""
        self.client.post(base_url + 'comments/1/',
                         self.comment_data, format='json')  # send POST to API
        self.response = self.client.patch(
            base_url + 'comments/1/', {'content_type_id': 2}, format='json')
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.comment_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(Comment.objects.filter(content_type_id=2)))

    def test_get_comment_request_returns_success(self):
        """Testing API can handle GET requests for Comment objects"""
        response = self.client.get(base_url + 'comments/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment_object.delete()  # delete object from temporary database
        # check that object was deleted from temporary database
        self.assertEqual(0, len(Comment.objects.filter(id=1)))

    def test_get_comments_view(self):
        json_request = {"chunk_id": self.chunk_object.id}
        response = self.client.post(
            base_url + 'get_comments/',
            json_request,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_that_api_can_delete_comment_objects(self):
        """Testing that the API has Comment Object deletion functionality"""
        response = self.client.delete(base_url + 'comments/1/')
        #200 and 204 are both valid return codes
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK or status.HTTP_204_NO_CONTENT)
        self.comment_object.delete()


