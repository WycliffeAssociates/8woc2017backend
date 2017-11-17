from django.test import TestCase
from django.db import IntegrityError

from api.models import Book

class TestBookModel(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        Book.objects.create(anthology_id=1,slug='mrk',name='Mark',number=42)

    
    def test_foreign_key_label(self):
        book=Book.objects.get(id=1)
        anthology_label=book._meta.get_field('anthology').verbose_name
        self.assertEqual(anthology_label,'anthology')

    def test_slug_label(self):
        book=Book.objects.get(id=1)
        slug_label=book._meta.get_field('slug').verbose_name
        self.assertEqual(slug_label,'slug')
    
    def test_slug_max_length(self):
        book=Book.objects.get(id=1)
        max_length=book._meta.get_field('slug').max_length
        self.assertEqual(max_length,50)

    def test_name_label(self):
        book=Book.objects.get(id=1)
        name_label=book._meta.get_field('name').verbose_name
        self.assertEqual(name_label,'name')
    
    def test_name_max_length(self):
        book=Book.objects.get(id=1)
        max_length=book._meta.get_field('name').max_length
        self.assertEqual(max_length,255)

    def test_number_label(self):
        book=Book.objects.get(id=1)
        number_label=book._meta.get_field('number').verbose_name
        self.assertEqual(number_label,'number')
    
    def test_number_default(self):
        book=Book.objects.get(id=1)
        default=book._meta.get_field('number').default
        self.assertEqual(default,0)

    def test_foreignkey_violation(self):
        with self.assertRaises(IntegrityError):
             Book.objects.create(slug='mrk',name='Mark',number=42)