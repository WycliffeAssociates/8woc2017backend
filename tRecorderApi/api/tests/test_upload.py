import os
import shutil

from django.test import TestCase

from ..file_transfer.FileUtility import FileUtility
from ..file_transfer.Upload import Upload
from ..file_transfer.ZipIt import ZipIt
from ..models import Take, Project, Chapter, Anthology, Language, Chunk, Mode, Version, Book


# to make this test work : create a new folder inside test, call it test_files, add a zip file and rename it to test
class UploadTestCases(TestCase):

    def test_create_root_directory(self):    #create a directory, verify if it exists and delete it
        fl = FileUtility()
        dir = fl.root_dir(['test', 'case'])
        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(dir)))
        is_dir = os.path.isdir(dir)
        shutil.rmtree(dir_path)
        self.assertEqual(True, is_dir)

    #TODO: Review this test case to better understand what it does, and how to
    # get it to work
    # def test_upload_zip(self):       # TODO remove the file created
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # file_to_upload = os.path.join(dir_path, 'test_files/test.zip')
        # up = Upload(ZipIt(), None, FileUtility())
        # resp, stat = up.upload(file_to_upload)
        # self.data_is_saved_in_DB()
        # self.assertEqual(resp, 'ok')
        # self.assertEqual(stat, 200)

    def data_is_saved_in_DB(self):
        project = Project.objects.all()
        take = Take.objects.all()
        chunk = Chunk.objects.all()
        chapter = Chapter.objects.all()
        anthology = Anthology.objects.all()
        language = Language.objects.all()
        book = Book.objects.all()
        version = Version.objects.all()
        mode = Mode.objects.all()

        self.assertEqual(len(project) > 0, True)
        self.assertEqual(len(take) > 0, True)
        self.assertEqual(len(chunk) > 0, True)
        self.assertEqual(len(chapter) > 0, True)
        self.assertEqual(len(anthology) > 0, True)
        self.assertEqual(len(language) > 0, True)
        self.assertEqual(len(version) > 0, True)
        self.assertEqual(len(book) > 0, True)
        self.assertEqual(len(mode) > 0, True)

    #TODO: Review test to better understand what it does, and how to get it to
    # work
    # def test_throws_exception(self):
        # fl = FileUtility()
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # file_to_upload = os.path.join(dir_path, 'test_files/test')
        # self.assertRaises(Exception, fl.import_project(file_to_upload))
