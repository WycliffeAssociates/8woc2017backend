from django.test import TestCase
from api.models import Comment
from api.views import CommentViewSet
from rest_framework.test import APIClient
from rest_framework import status

base_url = 'http://127.0.0.1:8000/api/'
my_file = 'media/dump'


class IntegrationCommentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.comment_object = Comment.objects.create(location='/test-location/', id=1)
        self.comment_data = {'location': 'test_location'}
        self.commentVS = CommentViewSet()

    def test_api_can_create_comment_object(self):
        """Test the API has comment creation capability:
        Sending JSON Comment Object To API and
        Expecting HTTP Success Message Returned"""
        self.response = self.client.post(base_url + 'comments/', self.comment_data, format='json')  # send POST to API
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_api_can_update_comment_object(self):
        """Test that the API can update a User object:
        Sending User Object To API and
        Expecting HTTP Success Message Returned"""
        self.comment_object.save()
        response = self.client.put(base_url + 'comments/1/', {'location': '/new-location/'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(Comment.objects.filter(id=1)))

    def test_get_comment_request_returns_success(self):
        """Testing API can handle GET requests for Comment objects"""
        self.comment_object.save()
        response = self.client.get(base_url + 'comments/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment_object.delete()  # delete object from temporary database
        self.assertEqual(0, len(Comment.objects.filter(id=1)))  # check that object was deleted from temporary database

    def test_that_api_can_delete_comment_objects(self):
        """Testing that the API has Comment Object deletion functionality"""
        self.comment_object.save()
        response = self.client.delete(base_url + 'comments/1/')
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)  # after deleting an object, nothing should be returned, which is why we check against a 204 status code
        self.comment_object.delete()
