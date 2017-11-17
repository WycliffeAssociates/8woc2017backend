from django.test import TestCase
from django.db import IntegrityError

from api.models import Language


class TestLanguageModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        Language.objects.create(slug='en', name='English')

    def test_slug_label(self):
        language = Language.objects.get(id=1)
        slug_label = language._meta.get_field('slug').verbose_name
        self.assertEquals(slug_label, 'slug')

    def test_slug_max_length(self):
        language = Language.objects.get(id=1)
        slug_max_length = language._meta.get_field('slug').max_length
        self.assertEquals(slug_max_length, 50)

    def test_name_label(self):
        language = Language.objects.get(id=1)
        name_label = language._meta.get_field('name').verbose_name
        self.assertEquals(name_label, 'name')

    def test_slug_max_length(self):
        language = Language.objects.get(id=1)
        name_max_length = language._meta.get_field('name').max_length
        self.assertEquals(name_max_length, 255)

    def test_get_language_with_parameter(self):
        result = Language.get_languages('en')
        self.assertEqual(result[0].slug, 'en')

    def test_get_language_without_parameter(self):
        result = Language.get_language()
        self.assertEqual(result[0].slug, 'en')

    def test_slug_is_unique(self):
        with self.assertRaises(IntegrityError):
            Language.objects.create(slug='en', name='English')
