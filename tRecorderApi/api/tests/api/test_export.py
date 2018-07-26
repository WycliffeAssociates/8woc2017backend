from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import os
from ...models import Language, Anthology, Book, Version, Mode, Project, Chapter, Chunk, Take

cur_path = os.path.dirname(__file__)
file_path = os.path.join(cur_path, "test_files", "zip", "abc.wav")


class ExportApiTest(TestCase):
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
            location=file_path,
            published=True,
            duration=0,
            markers="{\"test\" : \"true\"}",
            rating=2,
            chunk=self.chunk)

    #TODO: Review test to better understand what it does, and how to get it to
    # work
    # def test_download_zip_mp3_has_status_200_OK(self):
        # response = self.client.get('/api/export/?id=1&file_format=mp3/')
        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    #TODO: Review test to better understand what it does, and how to get it to
    # work
    # def test_download_zip_mp3_with_invalid_id_has_status_404_Not_Found(self):
        # # gives list of range error

        # response = self.client.get('/api/export/?id=2&file_format=mp3/')
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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
