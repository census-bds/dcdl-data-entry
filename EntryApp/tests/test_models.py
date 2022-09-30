from django.test import TestCase, SimpleTestCase
from django.db import IntegrityError

from EntryApp.models import Image, Breaker, Sheet, OtherImage, Record, CurrentEntry, FormField


class TestImageModel(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # set up data to be used in tests
        # TO DO: make a fixture instead?
        Image.objects.create(img_path='test_img.png', \
                            jbid='ajbid000', \
                            year=1960, \
                            image_type='sheet', \
                            is_complete=False)

    def test_uniqueness(self):
        # test that we can't enter an img_path/jbid combo more than once
        dup_img = Image(img_path='test_img.png', \
                        jbid='ajbid000', \
                        year=1960, \
                        image_type='sheet', \
                        is_complete=False)
        with self.assertRaises(IntegrityError):
            dup_img.save()


class TestBreakerModel(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # set up data to be used in tests
        # TO DO: make a fixture instead?
        breaker_img = Image(img_path='test_img.png', \
                            jbid='ajbid000', \
                            image_type='breaker')
        Breaker.objects.create(breaker_img, \
                            jbid='ajbid000')

    def test_uniqueness(self):
        # test that we can't enter an img_path/jbid combo more than once
        breaker_img = Image(img_path='test_img.png', \
                            jbid='ajbid000', \
                            image_type='breaker')
        breaker = Breaker(img = breaker_img, \
                         jbid='ajbid000')
        with self.assertRaises(IntegrityError):
            breaker.save()


class TestSheetModel(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        # set up data to be used in tests
        # TO DO: make a fixture instead?
        breaker_img = Image(img_path='test_img.png', \
                            jbid='ajbid000', \
                            image_type='breaker')
        Breaker.objects.create(breaker_img, \
                            jbid='ajbid000')

    def test_uniqueness(self):
        # test that we can't enter an img_path/jbid combo more than once
        breaker_img = Image(img_path='test_img.png', \
                            jbid='ajbid000', \
                            image_type='breaker')
        breaker = Breaker(img = breaker_img, \
                         jbid='ajbid000')
        with self.assertRaises(IntegrityError):
            breaker.save()
