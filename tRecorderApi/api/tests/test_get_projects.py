"""
    This module contains test cases for the retrieval of project data.
"""
from django.test import TestCase
from ..models import Project, Language, Book, Anthology, Version, Mode
from ..serializers import ProjectSerializer

class GetProjectsTestCases(TestCase):
    """
        Test cases which tests functions associated with retrieving data about
        projects.
    """
    def setUp(self):
        self.lang = Language.objects.create(
            slug='en-x-demo',
            name='english')
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
        self.project_serializer = ProjectSerializer(instance=self.proj)


    def test_keys_in_project(self):
        """
        Verify that the ProjectSerializer class serializes an object of type
        'Project' into a JSON format containing the following assumed keys:
            1)  id
            2)  published
            3)  contributors
            4)  date_modified
            5)  completed
            6)  checked_level
            7)  language
            8)  book
            9)  version
            10) anthology
        Input: data = serialized data of project object created in setup
        Expected: data will contain all of the keys listed above
        """
        data = self.project_serializer.data
        self.assertIn("id", data)
        self.assertIn("published", data)
        # self.assertIn("contributors", data)   project serializer does not
        # include this field
        self.assertIn("date_modified", data)
        self.assertIn("completed", data)
        # self.assertIn("checked_level", data) project field does not include
        # this field
        self.assertIn("language", data)
        self.assertIn("book", data)
        self.assertIn("version", data)
        self.assertIn("anthology", data)

    #TODO: This test seems to be test built-in django functions. Django
    # functions should not need to be tested by us. Please review this test to
    # see if it should be removed.
    # def test_get_minimum_checked_level(self):
        # min_check_level = Chapter.objects.all().values_list('checked_level') \
            # .order_by('checked_level')[0][0]
        # self.assertEqual(min_check_level, 0)

    #TODO: This function does not exist yet for the project class. Please
    # review to see if this test is still relevant.
    # def test_get_percentage_function(self):
        # """
        # Verify the 'Project' class's 'get_percentage_completed' function
        # behaves as expected.
        # Input: chunks_done = number of chunks ready for publishing within a
                             # chapter
               # total_chunks = total number of chunks within a chapter
        # Expected: function will return chunks_done/total_chunks represented as
                  # a whole number
        # """
        # chunks_done = 30
        # total_chunks = 100
        # percentage = Project.get_percentage_completed(chunks_done, total_chunks)
        # self.assertEqual(percentage, 30)

    def tearDown(self):
        self.lang.delete()
        self.anthology.delete()
        self.book.delete()
        self.version.delete()
        self.mode.delete()
        self.proj.delete()
