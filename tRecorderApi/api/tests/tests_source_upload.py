from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import Take
import os
from sys import platform

my_file = 'media/dump'
base_url = 'http://127.0.0.1:8000/api/'


class SourceFileUploadViewTestCases(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.take_object = Take(location=my_file, chapter=5, is_export=True, is_source=False, id=1, language_id=1,
                                book_id=1, user_id=1)

    def test_that_uploading_tr_file_with_wav_file_returns_200_OK(self):
        with open('en-x-demo2_ulb.tr', 'rb') as test_tr:
            self.response = self.client.post(base_url + 'source/en-x-demo2_ulb.tr', {'Media type': '*/*', 'Content': test_tr},
                                             format='multipart')
            self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_that_we_get_403_error_when_not_enough_parameters_are_uploaded_in_SourceFile(self):
        """Testing that submitting a POST request through book key search returns an object"""
        # saving objects in temporary database so they can be read by the API
        self.response = self.client.post(base_url + 'get_source/', {'book': 'book', 'book': 'book'},
                                    format='json')  # telling the API that I want all takes that are in book English
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)
        # freeing up the temporary database

    def test_that_we_get_403_error_when_no_source_is_uploaded_in_SourceFile(self):
        """Testing that submitting a POST request through book key search returns an object"""
        # saving objects in temporary database so they can be read by the API
        self.response = self.client.post(base_url + 'get_source/', {'language': 'eng', 'version': 'ulb'},
                                    format='json')  # telling the API that I want all takes that are in book English
        self.assertEqual(self.response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        if platform == "darwin": #OSX
            os.system('rm -rf ' + my_file)  # cleaning out all files generated during tests
            os.system('mkdir ' + my_file)
        elif platform == "win32": #Windows
            os.system('rmdir /s /q ' + 'media\dump')  # cleaning out all files generated during tests
            os.system('mkdir ' + 'media\dump')