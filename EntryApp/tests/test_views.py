from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
# from selenium.webdriver.chrome.webdriver import WebDriver

from http import HTTPStatus


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

import logging
logger = logging.getLogger('EntryApp.test_views')

DEV_FIXTURE =  'fixtures/dev_data_20211012_1543.json'
TEMP_USERNAME = 'jbid123'
TEMP_PW = 'dcdl1980'

class IndexViewTests(TestCase):

    fixtures = [DEV_FIXTURE]
    template_name = "index"

    @classmethod
    def setUpTestData(cls):
        pass


    def test_url_exists(self):
        ''' Test that the html response for this url is OK'''
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:index'), follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_code_image_button_present(self):
        ''' Test that the CodeImage button is present '''
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(reverse('EntryApp:index'), follow=True)

        # is the code image form action present?
        html_snippet = """<form action=/EntryApp/code-image/ method="post">"""
        self.assertTrue(html_snippet in str(response.content))

    
    def test_next_thumbnail_present(self):
        ''' Test that the thumbnail of next image is present '''
        pass


    def test_recent_image_queue_present(self):
        ''' Test that the recent image queue is present '''
        pass


class GetNextTests(TestCase):

    fixtures = [DEV_FIXTURE]
    
    @classmethod
    def setUpTestData(cls):
        pass

    def test_get_image_todo_qs(self):
        ''' Test method returns image queue as expected '''
        pass


class CodeImageTests(TestCase):

    fixtures = [DEV_FIXTURE]
    template_name = "code_image"

    @classmethod
    def setUpTestData(cls):
        pass

    def test_url_status_ok(self):
        ''' Test that the html response for this url is HTTPStatus.OK'''
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(
            reverse(f'EntryApp:{self.template_name}'),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)


    def test_image_is_present(self):
        ''' Test that openseadragon found an image '''
        pass


    def test_a_sheet_form_present(self):
        ''' Test that sheet form is present on first entering page '''
        self.client.login(username=TEMP_USERNAME, password=TEMP_PW)
        response = self.client.get(
            reverse(f'EntryApp:{self.template_name}'),
            follow=True
        )

        form_html = '''<form id="image-info" method="POST">'''
        self.assertTrue(form_html in str(response.content))

    
    def test_b_sheet_form_options(self):
        ''' Test that sheet form options match year '''
        pass


    def test_c_sheet_form_post(self):
        ''' Test that the sheet form POST method works '''
        pass


# class LoginSeleniumTests(StaticLiveServerTestCase):
    
#     fixtures = [DEV_FIXTURE]

#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.selenium = WebDriver()
#         cls.selenium.implicitly_wait(10)

#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super().tearDownClass()
    
#     def test_login(self):
#         self.selenium.get('%s%s' % (self.live_server_url, '/login/'))
#         username_input = self.selenium.find_element_by_name("username")
#         username_input.send_keys(TEMP_USERNAME)
#         password_input = self.selenium.find_element_by_name("password")
#         password_input.send_keys(TEMP_PW)
#         self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()