from django.test import TestCase
from .models import Take, Language, User, Comment, Book
from datetime import datetime


#Creating a text file to log the results of each of the tests
class ModelTestCase(TestCase):
    """This class defines the test suite for the each of the models."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.file_location = "uploads/file.zip"
        self.take = Take(location=self.file_location, is_source=False, is_export=True)
        self.language = Language(slug='abc', name='english')
        self.user = User(name='tester', agreed=True, picture='test.pic')
        self.comment = Comment(location='test_location')
        self.book = Book(slug='en-demo',name='english', booknum=5)

    def test_model_can_create_a_take(self):
        """Test the File model can create a take."""
        old_count = Take.objects.count()  #obtain current count of object in database
        self.take.save()   #save object to database
        new_count = Take.objects.count()  #obtain new count of object in database
        self.assertNotEqual(old_count, new_count)

    def test_model_can_create_a_Language(self):
        """Test the Language model can create a language."""
        old_count = Language.objects.count()
        self.language.save()
        new_count = Language.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_can_create_a_User(self):
        """Test the User model can create a user."""
        old_count = User.objects.count()
        self.user.save()
        new_count = User.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_can_create_a_Comment(self):
        """Test the Comment model can create a comment."""
        old_count = Comment.objects.count()
        self.comment.save()
        new_count = Comment.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_can_create_a_Book(self):
        """Test the Language model can create a language."""
        old_count = Book.objects.count()
        self.book.save()
        new_count = Book.objects.count()
        self.assertNotEqual(old_count, new_count)