from django.test import TestCase
from api.models import Take, Language, Book, User, Comment
from rest_framework.test import APIClient
from rest_framework import status

view_url = 'http://127.0.0.1:8000/api/all_project/'


class AllProjectViewTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.take_object = Take(chapter=5, version='ESV', is_export=True, is_source=False, id=1, language_id=1,
                                book_id=1, user_id=1)
        self.language_object = Language(slug='en-x-demo', name='english', id=1)
        self.book_object = Book(name='Mark', slug='en', booknum=5, id=1)
        self.user_object = User(name='testy', agreed=True, picture='mypic.jpg', id=1)
        self.comment_object = Comment(location='/test-location/', id=1)

    def test_post_request_for_all_projects_view(self):
        """Testing that sending a POST request to the All Project View returns a list of projects"""
        self.language_object.save()
        self.book_object.save()
        self.user_object.save()
        self.take_object.save()
        response = self.client.post(view_url, {'language': 'en-x-demo', 'version': 'ESV', 'book': 'en'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(0, len(response.data))  # checking that the response contains data
        self.take_object.delete()
        self.user_object.delete()
        self.book_object.delete()
