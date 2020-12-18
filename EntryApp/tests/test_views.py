from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from http import HTTPStatus

from EntryApp.models import Image, Breaker, CurrentEntry, Sheet
from EntryApp.forms import ImageForm, BreakerForm, SheetForm

import logging
logger = logging.getLogger('EntryApp.test_views')

TEMP_USERNAME = 'temp112'
TEMP_EMAIL = "temp@temp.com"
TEMP_PW = 'TEMP_PW1'

class IndexViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user = User.objects.create_user(TEMP_USERNAME, TEMP_EMAIL, TEMP_PW)

    def test_url_exists(self):
        ''' Test that the html response for this url is OK'''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
    

class BeginNewImageTests(TestCase):

    fixtures = ['image_dummy_data.json']

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user = User.objects.create_user(TEMP_USERNAME, TEMP_EMAIL, TEMP_PW)
        img = Image.objects.create(img_path='test_sheet.png', \
                                    jbid=TEMP_USERNAME, \
                                    image_type='breaker', \
                                    is_complete=False)
        breaker_img = Breaker.objects.create(img=img, \
                                            jbid=TEMP_USERNAME)
        print("setUpTestData complete")
 
    def test_a_url_exists(self):
        ''' Test that the html response for this url is HTTPStatus.OK'''
        print('testing url exists...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_b_get_next_image(self):
        ''' Test that the app loads next image into CurrentEntry as specified'''
        print('testing get_next_image...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(CurrentEntry.objects.get(jbid=TEMP_USERNAME).img.img_path, 'test_sheet.png') 

    def test_c_form_year_present(self):
        ''' Test that the year field is present in the form'''
        print('testing form_year_present...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(response.context['form'].fields['year'].label, 'Year') 

    def test_d_form_image_type_present(self):
        ''' Test that the image type field is present'''
        print('testing image type present...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(response.context['form'].fields['image_type'].label, 'Image type') 

    def test_e_form_post(self):
        print('testing begin new image post')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        CurrentEntry.objects.create(img=Image.objects.get(jbid=TEMP_USERNAME),
                                    jbid=TEMP_USERNAME,
                                    breaker=Breaker.objects.get(jbid=TEMP_USERNAME   ))
        response = self.client.post(
            reverse('EntryApp:begin_new_image'),
            {'year': 1960, 'image_type': 'breaker'}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/EntryApp/enter-breaker-data/")


class EnterBreakerDataTests(TestCase):
    pass


class SubmitBreakerTests(TestCase):
    pass


class EnterSheetDataTests(TestCase):
    pass


class SubmitSheetTests(TestCase):
    pass


class EnterRecordsTests(TestCase):
    pass


class SelectExportFormTests(TestCase):
    pass


class ExportRecordsTests(TestCase):
    pass
