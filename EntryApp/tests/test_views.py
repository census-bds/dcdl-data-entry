from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from EntryApp.models import Image, Breaker, CurrentEntry, Sheet
from EntryApp.forms import ImageForm, BreakerForm, SheetForm

import logging
logger = logging.getLogger('EntryApp.test_views')

TEMP_USERNAME = 'temp111'
TEMP_EMAIL = "temp@temp.com"
TEMP_PW = 'TEMP_PW1'

class IndexViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user = User.objects.create_user(TEMP_USERNAME, TEMP_EMAIL, TEMP_PW)

    def test_url_exists(self):
        ''' Test that the html response for this url is 200'''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:index'))
        self.assertEqual(response.status_code, 200)
    

class BeginNewImageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        user = User.objects.create_user(TEMP_USERNAME, TEMP_EMAIL, TEMP_PW)
        img = Image(img_path='test_sheet.png', \
                    jbid=TEMP_USERNAME, \
                    image_type='breaker', \
                    is_complete=False)
        breaker_img = Breaker(img=img, \
                    jbid=TEMP_USERNAME)
        img.save()
        breaker_img.save()
        # CurrentEntry.objects.create(img=img, \
        #                             jbid=TEMP_USERNAME, \
        #                             breaker=breaker_img)

    def test_url_exists(self):
        ''' Test that the html response for this url is 200'''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(response.status_code, 200)

    def test_get_next_image(self):
        ''' Test that the app loads next image into CurrentEntry as specified'''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(CurrentEntry.objects.get(jbid=TEMP_USERNAME).img.img_path, 'test_sheet.png') 

    def test_form_year_present(self):
        ''' Test that the year field is present in the form'''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(response.context['form'].fields['year'].label, 'Year') 

    def test_form_image_type_present(self):
        ''' Test that the image type field is present'''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:begin_new_image'))
        self.assertEqual(response.context['form'].fields['image_type'].label, 'Image type') 

    def test_image_form(self):
        ''' Test that the app can submit data for the image specified '''
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)

        # make an instance of image form
        f = {'year': 1960, 'image_type': 'breaker'}
        # f.fields['year'] = 1960
        # f.fields['image_type'] = 'breaker'
        response = self.client.post(reverse('EntryApp:begin_new_image'), kwargs=f)
        logger.info(f'test_image_form response is {response.content}')
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(CurrentEntry.objects.get(jbid=TEMP_USERNAME).img.img_path, 'test_image.png')




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
