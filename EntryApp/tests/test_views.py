#===============================================================#
# TEST ENTRYAPP VIEWS
#===============================================================#

import logging

from bs4 import BeautifulSoup
from http import HTTPStatus

# django imports
from django.conf import settings
from django.forms import modelformset_factory
from django.test import TestCase
from django.urls import get_script_prefix
from django.urls import reverse

# EntryApp models
from EntryApp.models import Breaker
from EntryApp.models import CurrentEntry
from EntryApp.models import FormField
from EntryApp.models import Image
from EntryApp.models import ImageFile
from EntryApp.models import Keyer
from EntryApp.models import LongForm1990
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Reel
from EntryApp.models import Sheet

# EntryApp forms
from EntryApp.forms import BaseBreakerFormSet
from EntryApp.forms import BaseEmptyRecordFormSet
from EntryApp.forms import BaseRecordFormSet
from EntryApp.forms import CrispyFormSetHelper
from EntryApp.forms import CrispyLongFormHelper
from EntryApp.forms import ImageForm
from EntryApp.forms import LongForm1990Form
from EntryApp.forms import LongFormHelper
from EntryApp.forms import OtherImageForm
from EntryApp.forms import ProblemForm
from EntryApp.forms import RecordForm
from EntryApp.forms import RecordFormHelper
from EntryApp.forms import SheetForm

# user creation and DB load methods
import EntryApp.create_users as users
import EntryApp.load_db as ldb
import EntryApp.tests.test_utils as utils
import EntryApp.tests.expected_values as expected

#================================#
# LOGGER
#================================#

logger = logging.getLogger('EntryApp.test_views')

#================================#
# GLOBALS
#================================#

DEV_FIXTURE =  'fixtures/dev_data_20220412_1418.json'
TEMP_USERNAME = 'jbid456'
TEMP_PW = 'dcdl1980'

EXPECTED = expected.DATA[DEV_FIXTURE][TEMP_USERNAME]


#================================#
# BASE CLASS
#================================#

class BaseTestCase(TestCase):

    fixtures = [DEV_FIXTURE]
    template_name = None

    @classmethod
    def setUpTestData(cls):
        pass

    def authenticate_and_get_response(self):
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        return self.client.get(reverse(self.template_name), follow=True)

    def authenticate_and_post(self, context=None):
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        return self.client.post(reverse(self.template_name), context, follow=True)


#================================#
# TEST CASES
#================================#

class IndexViewTests(BaseTestCase):

    template_name = "EntryApp:index" # this is a class variable not instance, think about it


    def test_url_exists(self):
        ''' Test that the html response for this url is OK'''
        response = self.authenticate_and_get_response()
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_user_has_reel(self):
        ''' Test that the user has the expected reel+images assigned '''
        response =  self.authenticate_and_get_response()

        current = CurrentEntry.objects.get(jbid = TEMP_USERNAME)

        self.assertEqual(current.reel_id, EXPECTED['current_reel_id']) 
        self.assertEqual(current.image_file_id, EXPECTED['current_image_file_id'])
        self.assertEqual(current.img_id, EXPECTED['current_img_id'])


    def test_code_image_button_present(self):
        ''' Test that the CodeImage button is present '''
        response = self.authenticate_and_get_response()
        response = self.client.get(reverse(self.template_name), follow=True)

        # is the code image form action present?
        html_snippet = """<form action=/EntryApp/code-image/ method="post">"""
        self.assertTrue(html_snippet in str(response.content))

    
    def test_image_present(self):
        ''' Test that the thumbnail of next image is present '''
        response = self.authenticate_and_get_response()

        # grab the image url from the page
        # try to follow that url
        # assert that the status code is 200
        soup = BeautifulSoup(response.content, 'html.parser')
        img_url = soup.body.find("img")['src']
        img_response = self.client.get(img_url)

        self.assertEqual(img_url, EXPECTED['img_url'])

        # this fails right now but works in browser: 
        # the path needs to be localhost:8002/images, NOT localhost:8002/EntryApp/images 
        self.assertEqual(img_response.status_code, HTTPStatus.OK)


    def test_load_next_batch(self):
        ''' Test load next batch POST request '''
        pass

        # verify that the values of num_images, num_completed, num_todo are correct
        #   - check for middle of reel (i.e. batch size <= # remaining images)
        #   - check for end of reel (batch_size > # remaining images)
        # using a fixture at the end of a batch, verify that a post request will advance us


    def test_load_next_reel(self):
        ''' Test load next reel POST request '''

        # use a fixture at the end of a reel, verify that a POST request does advance us
        # - check that all the correct tables get updated


class GetNextTests(BaseTestCase):

    def test_method(self):
        pass


class CodeImageTests(BaseTestCase):

    fixtures = [DEV_FIXTURE]
    template_name = "EntryApp:code_image"

    def test_url_status_ok(self):
        ''' Test that the html response for this url is HTTPStatus.OK'''
        response = self.authenticate_and_get_response()
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_a_image_form_present(self):
        ''' Test that image form is present on first entering page '''

        context = EXPECTED['code_image_test_a_context']
        context['image_form'] = ImageForm(
             EXPECTED['year'],
             EXPECTED['current_reel_name'],
             EXPECTED['code_image_test_a_context']['image_form_values']
            )    
        response = self.authenticate_and_post(context=context)

        form_html = '''<form id="image-info"'''
        self.assertTrue(form_html in str(response.content))

    
    def test_b_sheet_form_options(self):
        ''' Test that sheet form options match year '''
        pass


    def test_c_sheet_type_breaker_post(self):
        ''' Test a post request when sheet_type is breaker '''
        response = self.authenticate_and_get_response()

        # post request should have okay status
        post_response = self.client.post(
            reverse(self.template_name),
            EXPECTED['sheet_type_breaker_post']
        ) 
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        # should also update database
        image = Image.objects.get(id = EXPECTED['sheet_type_breaker_post']['image_id'])
        self.assertEqual(image.image_type, 'breaker')


    #TODO: abstract to reduce redundancy here
    def test_d_sheet_type_other_post(self):
        ''' Test a post request when sheet_type is other '''
        response = self.authenticate_and_get_response()

        # post request should have okay status
        post_response = self.client.post(
            reverse(self.template_name),
            EXPECTED['sheet_type_other_post']
        ) 
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        # should also update database
        image = Image.objects.get(id = EXPECTED['sheet_type_other_post']['image_id'])
        self.assertEqual(image.image_type, 'other')


    #TODO: abstract to reduce redundancy here
    def test_e_sheet_type_sheet_post(self):
        ''' Test a post request when sheet_type is sheet '''
        response = self.authenticate_and_get_response()

        # post request should have okay status
        post_response = self.client.post(
            reverse(self.template_name),
            EXPECTED['sheet_type_sheet_post']
        ) 
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        # should also update database
        image = Image.objects.get(id = EXPECTED['sheet_type_sheet_post']['image_id'])
        self.assertEqual(image.image_type, 'sheet')
