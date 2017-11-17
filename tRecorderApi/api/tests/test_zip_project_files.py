from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status

base_url = 'http://127.0.0.1:8000/api/'


class TestZipProjectFiles(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_should_return_http_status_200(self):
        self.response = self.client.post(base_url + 'zip_project_files/',
                         {
                         "language": "en-x-demo2",
                         "version": "ulb",
                         "book": "mrk"
                         }, format='json')

        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_should_return_http_status_400(self):
        self.response=self.client.post(base_url + 'zip_project_files/',
                         {
                         "language": "en-x-demo2",
                         "version": "ulb",
                         "book": "m"
                         },format='json')
        
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)
