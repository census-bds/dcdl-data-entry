from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory

from http import HTTPStatus

from EntryApp.models import Image, Breaker, CurrentEntry, Sheet
from EntryApp.forms import ImageForm, BreakerForm, SheetForm, BaseBreakerFormSet

import EntryApp.tests.test_utils as utils

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
    template_name = 'EntryApp:begin_new_image'

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
        response = self.client.get(reverse(self.template_name))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_b_get_next_image(self):
        ''' Test that the app loads next image into CurrentEntry as specified'''
        print('testing get_next_image...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse(self.template_name))
        self.assertEqual(CurrentEntry.objects.get(jbid=TEMP_USERNAME).img.img_path, 'test_sheet.png') 

    def test_c_form_year_present(self):
        ''' Test that the year field is present in the form'''
        print('testing form_year_present...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse(self.template_name))
        self.assertEqual(response.context['form'].fields['year'].label, 'Year') 

    def test_d_form_image_type_present(self):
        ''' Test that the image type field is present'''
        print('testing image type present...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse(self.template_name))
        self.assertEqual(response.context['form'].fields['image_type'].label, 'Image type') 

    def test_e_form_post_breaker(self):
        print('Test that the page successfully redirects to breaker entry')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        CurrentEntry.objects.create(img=Image.objects.get(jbid=TEMP_USERNAME),
                                    jbid=TEMP_USERNAME,
                                    breaker=Breaker.objects.get(jbid=TEMP_USERNAME   ))
        response = self.client.post(
            reverse(self.template_name),
            {'year': [1960], 'image_type': ['breaker']}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/EntryApp/enter-breaker-data/")

    def test_f_form_post_sheet(self):
        print('Test that the page successfully redirects to sheet entry')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        CurrentEntry.objects.create(img=Image.objects.get(jbid=TEMP_USERNAME),
                                    jbid=TEMP_USERNAME,
                                    breaker=Breaker.objects.get(jbid=TEMP_USERNAME   ))
        response = self.client.post(
            reverse(self.template_name),
            {'year': [1960], 'image_type': ['sheet']}
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, "/EntryApp/enter-sheet-data/")


class EnterBreakerDataTests(TestCase):
    
    fixtures = ['image_dummy_data.json']
    template_name = 'EntryApp:enter_breaker_data'

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
        current = CurrentEntry.objects.create(jbid=TEMP_USERNAME, \
                                            img=img, \
                                            breaker = breaker_img, \
                                            sheet = None)
    
    def test_a_url_exists(self):
        ''' Test that the html response for this url is HTTPStatus.OK'''
        print('testing url exists...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse(self.template_name))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_b_formset_present(self):
        ''' Test that the formset is present in the view'''
        print('testing form_year_present...')
        User = get_user_model()
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse(self.template_name))
        self.assertIsNotNone(response.context['formset'])

    # def test_e_form_post(self):
    #     ''' Test that breaker view redirects to index after submission '''
    #     User = get_user_model()
    #     self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
    #     response = self.client.get(reverse(self.template_name))
    #     self.assertEqual(response.status_code, HTTPStatus.OK)
        
    #     data = [{'state': ['CA'], 'county': ['Alameda']}]
    #     post_data = utils.create_formset_post_data(response, new_form_data=data)
    #     response = self.client.post(
    #         reverse(self.template_name),
    #         post_data
    #     )
    #     self.assertEqual(response.status_code, HTTPStatus.FOUND)
    #     self.assertEqual(response.url, "/EntryApp/")

    # def test_f_breaker_data_submission(self):
    #     ''' Test that submitted data is saved to DB '''
    #     User = get_user_model()
    #     self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
    #     response = self.client.post(
    #         reverse(self.template_name),
    #         {'state': ['OH'], 'county': ['Cuyahoga']}
    #     )
    #     latest = Breaker.objects.filter(jbid=TEMP_USERNAME) \
    #                             .order_by('-timestamp')[0]
    #     print(latest)
    #     self.assertEqual(latest.state, 'OH')
        # self.assertEqual(latest.county, 'Cuyahoga')


class EnterSheetDataTests(TestCase):
    pass



class EnterRecordsTests(TestCase):
    pass


class SelectExportFormTests(TestCase):
    pass


class ExportRecordsTests(TestCase):
    pass
