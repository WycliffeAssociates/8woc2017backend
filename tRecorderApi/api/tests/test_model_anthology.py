from django.test import TestCase
from django.db import IntegrityError

from api.models import Anthology

class TestAnthologyModel(TestCase):
    

    @classmethod
    def setUpTestData(cls):
        Anthology.objects.create(slug='bs',name='Bible Story')

    def test_slug_label(self):
        version=Anthology.objects.get(id=1)
        slug_label=version._meta.get_field('slug').verbose_name
        self.assertEquals(slug_label,'slug')

    def test_slug_max_length(self):
        version=Anthology.objects.get(id=1)
        slug_max_length=version._meta.get_field('slug').max_length
        self.assertEquals(slug_max_length,50)

    def test_name_label(self):
        version=Anthology.objects.get(id=1)
        name_label=version._meta.get_field('name').verbose_name
        self.assertEquals(name_label,'name')

    def test_name_max_length(self):
        version=Anthology.objects.get(id=1)
        name_max_length=version._meta.get_field('name').max_length
        self.assertEquals(name_max_length,255)

    def test_get_version_without_parameter(self):
        result=Anthology.get_anthologies()
        self.assertEqual(result[0].slug,'bs')

    def test_get_version_with_parameter(self):
        result=Anthology.get_anthologies("bs")
        self.assertEqual(result[0].slug,'bs')    

    def test_slug_is_unique(self):
         with self.assertRaises(IntegrityError):
              Anthology.objects.create(slug='bs',name='Bible Story')
    