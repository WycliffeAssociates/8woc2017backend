from api.models import Version
from django.test import TestCase
from django.db import IntegrityError

class TestVersionModel(TestCase):
    """
    This class tests model version
    """

    @classmethod
    def setUpTestData(cls):
       Version.objects.create(slug='ulb',name='Unlocked Literal Bible')
        
    def test_slug_label(self):
        version=Version.objects.get(id=1)
        slug_label=version._meta.get_field('slug').verbose_name
        self.assertEquals(slug_label,'slug')

    def test_slug_max_length(self):
        version=Version.objects.get(id=1)
        slug_max_length=version._meta.get_field('slug').max_length
        self.assertEquals(slug_max_length,50)

    def test_name_label(self):
        version=Version.objects.get(id=1)
        name_label=version._meta.get_field('name').verbose_name
        self.assertEquals(name_label,'name')

    def test_slug_max_length(self):
        version=Version.objects.get(id=1)
        name_max_length=version._meta.get_field('name').max_length
        self.assertEquals(name_max_length,255)

    def test_get_versions_without_parameter(self):
        result=Version.get_versions()
        self.assertEquals(result[0].slug,'ulb')

    def test_get_versions_with_parameter(self):
        result=Version.get_version('ulb')
        self.assertEquals(result[0].slug,'ulb')

    def test_slug_is_unique(self):
        with self.assertRaises(IntegrityError):
             Version.objects.create(slug='ulb',name='Unlocked Literal Bible')