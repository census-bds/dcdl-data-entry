#===============================================================#
# TEST ENTRYAPP VIEWS
#===============================================================#

import logging
import unittest

from bs4 import BeautifulSoup
from http import HTTPStatus

# django imports
from django.conf import settings
from django.db import transaction
from django.forms import modelformset_factory
from django.test import TestCase
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
from EntryApp.forms import BreakerFormHelper
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

# EntryApp views
from EntryApp.views import get_form_fields

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

DEV_FIXTURE =  'fixtures/dev_data_2022-05-12.json'
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

    def authenticate_and_get_response(self, context=None):
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        return self.client.get(reverse(self.template_name), context, follow=True)

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

        print(img_url)

        # img_response = self.client.get("/data/data/images/dev/1960/dev_1960/fake_IMG_2_smaller.jpg")

        # this fails right now but works in browser: 
        # the path needs to be localhost:8002/images, NOT localhost:8002/EntryApp/images 
        # self.assertEqual(img_response.status_code, HTTPStatus.OK)


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
        pass


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

    
    def test_b_image_type_options(self):
        ''' 
        Test that the expected radio buttons show up in html for 
        image type selection 
        '''

        post_response = self.authenticate_and_post(
            context=EXPECTED['image_type_sheet_post']
        )

        form_html = str(post_response.content)
        expected_radio_options = EXPECTED['image_type_options']

        for e in expected_radio_options:
            self.assertTrue(e in form_html)


    def test_c_image_type_breaker_post(self):
        ''' Test a post request when image_type is breaker '''

        # post request should have okay status
        post_response = self.authenticate_and_post(
            context=EXPECTED['image_type_breaker_post']
        ) 
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        # should also update database
        image = Image.objects.get(id = EXPECTED['image_type_breaker_post']['image_id'])
        self.assertEqual(image.image_type, 'breaker')


    #TODO: abstract to reduce redundancy here
    def test_d_image_type_other_post(self):
        ''' Test a post request when image_type is other '''

        # post request should have okay status
        post_response = self.authenticate_and_post(
            EXPECTED['image_type_other_post']
        ) 
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        # should also update database
        image = Image.objects.get(id = EXPECTED['image_type_other_post']['image_id'])
        self.assertEqual(image.image_type, 'other')


    #TODO: abstract to reduce redundancy here
    def test_e_image_type_sheet_post(self):
        ''' Test a post request when image_type is sheet '''

        # post request should have okay status
        post_response = self.authenticate_and_post(
            EXPECTED['image_type_sheet_post']
        ) 
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        # should also update database
        image = Image.objects.get(id = EXPECTED['image_type_sheet_post']['image_id'])
        self.assertEqual(image.image_type, 'sheet')


class CodeImageBreakerTests(BaseTestCase):

    fixtures = [DEV_FIXTURE]
    template_name = "EntryApp:code_image"

    def test_breaker_prepare_context(self):
        '''Test that breaker form appears in context '''

        context = EXPECTED['breaker_data_entry']
        response = self.authenticate_and_post(context=context)
 
        html_to_find = '<div id="div_id_form-0-enumeration_district"'
        self.assertTrue(html_to_find in str(response.content))
 
    @unittest.skip("not working right now bc formset issue")
    def test_breaker_data_entry(self):
        '''Test ability to submit data about breaker'''
        pass
        # NOT WORKING RIGHT NOW, SEE THIS
        # https://stackoverflow.com/questions/1630754/django-formset-unit-test

        expected = EXPECTED['breaker_data_entry']
        context = expected
        context['action'] = 'update_breaker_type'

        image = Image.objects.get(id=expected['image_id'])
        breaker_qs = image.breaker_set.all()
        formset_extra_count = 0

        # set up form.
        breaker_fields = get_form_fields(1960, 'breaker')

        BreakerFormSet = modelformset_factory(
            Breaker,
            fields = breaker_fields,
            formset = BaseBreakerFormSet,
            extra = formset_extra_count
        )
        formset = BreakerFormSet( queryset = breaker_qs )

        if formset.is_valid():
            context[ 'breaker_formset' ] = formset

        post_response = self.authenticate_and_post(context=context)
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        breaker = Breaker.objects.get(id = expected['breaker_id'])
        self.assertEqual(breaker.year, expected['year'])
        self.assertEqual(breaker.state, expected['state'])



class CodeImageSheetTests(BaseTestCase):

    fixtures = [DEV_FIXTURE]
    template_name = "EntryApp:code_image"

    def test_sheet_integrity_error(self):
        '''Test what happens if they hit submit twice on sheet info'''

        expected = EXPECTED['code_image_test_f_sheet_integrity_error']
        context = expected

        # first, create and submit duplicate sheet, trigger IntegrityError
        context['sheet_form'] = SheetForm()   
        context['num_records'] = 20 
        response = self.authenticate_and_post(context=context)

        # then verify that the DB did not update
        sheet_instance = Sheet.objects.get(id=expected['sheet_id'])
        self.assertNotEqual(context['num_records'], sheet_instance.num_records)

        # check that the error message is in the content
        error_message = "In CodeImage.action_update_sheet(): sheet already exists. If the record entry block did not appear, please go back to the home page and resume coding this image from there."
        self.assertTrue(error_message in str(response.content))


    def test_sheet_data_entry(self):
        '''Test entry form for sheet-level data'''

        post_response = self.authenticate_and_post(
            context=EXPECTED['sheet_data_entry']
        )
        self.assertEqual(post_response.status_code, HTTPStatus.OK)

        sheet = Sheet.objects.get(id = EXPECTED['sheet_data_entry']['sheet_id'])
        self.assertEqual(sheet.num_records, EXPECTED['sheet_data_entry']['num_records'])


class ReportProblemTests(BaseTestCase):

    fixtures = [DEV_FIXTURE]
    template_name = "EntryApp:report_problem"


    def test_url_status_ok(self):
        '''test that GET request returns 200'''

        context = EXPECTED['report_problem']
        response = self.authenticate_and_get_response(context)
        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_image_present(self):
        '''Test that the relevant image appears on page'''

        context = EXPECTED['report_problem']
        response = self.authenticate_and_get_response(context)
        
        item_in_html = 'div id="openseadragon1"'
        self.assertTrue(item_in_html in str(response.content))


    def test_form_present(self):
        '''Test that the problem box appears on the page'''

        context = EXPECTED['report_problem']
        response = self.authenticate_and_get_response(context)
        
        item_in_html = '<div id="problem-form">'
        self.assertTrue(item_in_html in str(response.content))

    
    def test_report_submit(self):
        '''Test that submitted data ends up in DB'''
        
        expected = EXPECTED['report_problem']
        context = expected

        response = self.authenticate_and_post(context)
        
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # now get image out of DB
        image = Image.objects.get(id=expected['image_id'])

        self.assertTrue(image.problem)
        self.assertEqual(image.prob_description, expected.get('description')[0])
    
