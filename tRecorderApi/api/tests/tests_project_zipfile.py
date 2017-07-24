from django.test import TestCase
from api.models import Take, Language, Book, User, Comment
from rest_framework.test import APIClient
from rest_framework import status
import os
from sys import platform
import os.path

view_url = 'http://127.0.0.1:8000/api/zipFiles/'
upload_url = 'http://127.0.0.1:8000/api/upload/zip'
my_file = 'en-x-demo2_ulb_b42_mrk_c06_v01-03_t11.wav'


class ProjectZipFileViewTestCases(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.take_object = Take(location=my_file, chapter=5, version='ESV', is_export=True, is_source=False, id=1,
                                language_id=1, book_id=1, user_id=1)
        self.language_object = Language(slug='en-x-demo', name='english', id=1)
        self.book_object = Book(name='Mark', slug='en', booknum=5, id=1)
        self.user_object = User(name='testy', agreed=True, picture='mypic.jpg', id=1)
        self.comment_object = Comment(location='/test-location/', id=1)

    def test_post_request_for_project_zip_file_view(self):
        """POST request for Project Zip File view expects a wav file as input, and will return a zip file"""
        self.language_object.save()
        self.book_object.save()
        self.user_object.save()
        self.take_object.save()
        old_folder_size = len(os.listdir('media/export'))  # find the total number of files in the media/export folder
        response = self.client.post(view_url, {'language': 'en-x-demo', 'version': 'ESV', 'book': 'en'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # making sure that we return the correct status code
        new_folder_size = len(os.listdir('media/export'))  # new zip file should have been added to media/export folder
        self.assertNotEqual(old_folder_size, new_folder_size)  # check that a new file exists in media/export
        self.take_object.delete()
        self.user_object.delete()
        self.book_object.delete()

    def test_posting_file_to_api_returns_success_response(self):
        """Testing That zip files can be uploaded to the api"""
        with open('en-x-demo2_ulb_mrk.zip', 'rb') as test_zip:
            self.response = self.client.post(upload_url, {'Media type': '*/*', 'Content': test_zip},
                                             format='multipart')
            self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_that_we_get_403_error_when_not_enough_parameters_in_ProjectZipFile(self):
        """Testing that submitting a POST request through book key search returns an object"""
        # saving objects in temporary database so they can be read by the API
        self.response = self.client.post(view_url, {'language': 'eng', 'version': 'ulb'},
                                    format='json')  # telling the API that I want all takes that are in book English
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)

    def test_that_we_get_202_when_enough_parameters_in_ProjectZipFile(self):
        """Testing that submitting a POST request through book key search returns an object"""
        # saving objects in temporary database so they can be read by the API
        self.response = self.client.post(view_url, {'language': 'eng', 'version': 'ulb', 'book':'gen'},
                                    format='json')  # telling the API that I want all takes that are in book English
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def tearDown(self):
        if platform == "darwin":  # OSX
            os.system('rm -rf ' + 'media/export')  # cleaning out all files generated during tests
            os.system('mkdir ' + 'media/export')
        elif platform == "win32":  # Windows
            os.system('rmdir /s /q ' + 'media\export')  # cleaning out all files generated during tests
            os.system('mkdir ' + 'media\export')
