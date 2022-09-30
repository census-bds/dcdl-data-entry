"""
VIEWS FOR DCDL DATA ENTRY APPLICATION
"""

# python imports
import datetime
import json
import logging
import re


# django imports
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Q
import django.forms as forms
from django.forms import modelform_factory
from django.forms import modelformset_factory
from django.forms import RadioSelect
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import loader
from django.template import RequestContext
from django.template.context_processors import csrf
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import View

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
from EntryApp.forms import BreakerFormHelper
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
from EntryApp.forms import SheetFormHelper

# EntryApp choices
import EntryApp.choices as choices


#==============================================================================#
# CONSTANTS-ish
#==============================================================================#

# image batch size
BATCH_SIZE = 25

# standard context names
CONTEXT_BREAKER_INSTANCE = "breaker_instance"
CONTEXT_BREAKER_FORMSET = "breaker_formset"
CONTEXT_BREAKER_FORM_HELPER = "breaker_helper"
CONTEXT_FORM_HELPER = "helper"
CONTEXT_LONGFORM_INSTANCE = "longform_instance"
CONTEXT_LONGFORM_FORM = "longform_form"
CONTEXT_LONGFORM_HELPER = "helper"
CONTEXT_PARAM_NAMES = "param_names"
CONTEXT_PAGE_STATUS_MESSAGE_LIST = "page_status_message_list"
CONTEXT_OTHER_IMAGE_INSTANCE = "other_image_instance"
CONTEXT_OTHER_IMAGE_FORM = "other_image_form"
CONTEXT_RECORD_INSTANCE = "record_instance"
CONTEXT_RECORD_FORM = "record_form"
CONTEXT_RECORD_FORMSET_HELPER = "record_helper"
CONTEXT_RECORD_LIST = "record_list"
CONTEXT_SHEET_INSTANCE = "sheet_instance"
CONTEXT_SHEET_FORM = "sheet_form"
CONTEXT_SHEET_HELPER = "sheet_helper"
CONTEXT_USERNAME = "username"

# input parameter names
PARAM_NAME_ACTION = "action"
PARAM_NAME_BREAKER_ID = "breaker_id"
PARAM_NAME_IMAGE_ID = "image_id"
PARAM_NAME_IMAGE_TYPE = "image_type"
PARAM_NAME_LONGFORM_ID = "longform_id"
PARAM_NAME_OTHER_IMAGE_ID = "other_image_id"
PARAM_NAME_RECORD_ID = "record_id"
PARAM_NAME_SHEET_ID = "sheet_id"
PARAM_NAME_YEAR = "year"
PARAM_NAMES = {}
PARAM_NAMES[ "PARAM_NAME_ACTION" ] = PARAM_NAME_ACTION
PARAM_NAMES[ "PARAM_NAME_BREAKER_ID" ] = PARAM_NAME_BREAKER_ID
PARAM_NAMES[ "PARAM_NAME_IMAGE_ID" ] = PARAM_NAME_IMAGE_ID
PARAM_NAMES[ "PARAM_NAME_IMAGE_TYPE" ] = PARAM_NAME_IMAGE_TYPE
PARAM_NAMES[ "PARAM_NAME_LONGFORM_ID" ] = PARAM_NAME_LONGFORM_ID
PARAM_NAMES[ "PARAM_NAME_OTHER_IMAGE_ID" ] = PARAM_NAME_OTHER_IMAGE_ID
PARAM_NAMES[ "PARAM_NAME_RECORD_ID" ] = PARAM_NAME_RECORD_ID
PARAM_NAMES[ "PARAM_NAME_SHEET_ID" ] = PARAM_NAME_SHEET_ID
PARAM_NAMES[ "PARAM_NAME_YEAR" ] = PARAM_NAME_YEAR

# actions for CodeImageView
ACTION_COMPLETE_IMAGE = "complete_image"
ACTION_EDIT_RECORD = "edit_record"
ACTION_UPDATE_BREAKER_TYPE = "update_breaker_type"
ACTION_UPDATE_IMAGE = "update_image"
ACTION_UPDATE_LONGFORM = "update_longform"
ACTION_UPDATE_OTHER_IMAGE = "update_other_image"
ACTION_UPDATE_SHEET_TYPE = "update_sheet_type"
ACTION_UPDATE_RECORD = "update_record"
VALID_ACTIONS = []
VALID_ACTIONS.append( ACTION_COMPLETE_IMAGE )
VALID_ACTIONS.append( ACTION_EDIT_RECORD )
VALID_ACTIONS.append( ACTION_UPDATE_BREAKER_TYPE )
VALID_ACTIONS.append( ACTION_UPDATE_IMAGE )
VALID_ACTIONS.append( ACTION_UPDATE_LONGFORM )
VALID_ACTIONS.append( ACTION_UPDATE_OTHER_IMAGE )
VALID_ACTIONS.append( ACTION_UPDATE_SHEET_TYPE )
VALID_ACTIONS.append( ACTION_UPDATE_RECORD )

# actions for IndexView
ACTION_LOAD_NEXT_BATCH = "load_next_batch"
ACTION_LOAD_NEXT_REEL = "load_next_reel"
INDEX_ACTIONS = []
INDEX_ACTIONS.append( ACTION_LOAD_NEXT_BATCH )
INDEX_ACTIONS.append( ACTION_LOAD_NEXT_REEL )

#==============================================================================#
# LOGGER
#==============================================================================#

logger = logging.getLogger(__name__)

class CustomAdapter(logging.LoggerAdapter):
    ''' Custom class for adding keyer id to log output '''

    def process(self, msg, kwargs):
        extra_info = kwargs.pop('user', self.extra['user'])
        return '%s %s' % (extra_info, msg), kwargs

adapter = CustomAdapter(logger, {'user': "_"})

#==============================================================================#
# HELPER METHODS
#==============================================================================#

def get_form_fields( year, form_type ):
    '''
    Looks up the fields that a given form needs to display in FormFields

    Takes: 
    - int year (must be 1960, 1970, 1980, or 1990)
    - string form_type (must be breaker or record)
    Returns:
    - list of fields 
    '''

    allowed_years = [1960, 1970, 1980, 1990, ]
    allowed_forms = ['breaker', 'short', 'long', 'sheet', ]
    
    adapter.info(
        f"get_form_fields got {year}, {form_type}",
        # {'user': '_'}
    )

    if year in allowed_years and form_type in allowed_forms:

        field_query = FormField.objects.filter(year=year).filter(form_type=form_type)
        adapter.info(
            f'FormField query length was {len(field_query)}',
            # {'user': '_'}
        )
        
        return [f.field_name for f in list(field_query)]

    else:

        adapter.info(
            f'Invalid argument for get_fields: {year} {form_type}',
            # {'user': '_'}
        )
        
        return []


def make_batch_done_true(keyer_jbid):
    '''
    Helper method to track whether last image in batch is done
    Method should be called when an image is completed

    Takes:
    - string keyer jbid
    Returns:
    - None
    '''

    adapter.info(
        f'setting current.batch_position for {keyer_jbid} to 1',
        {'user': keyer_jbid}
    )

    try:
        # now update CurrentEntry batch position
        current = CurrentEntry.objects.get(jbid = keyer_jbid)
        current.batch_position = 1 
        current.save()

    except:

        adapter.exception(
            f'error when setting current batch status - does keyer row exist?',
            {'user': keyer_jbid}
        )


def compute_batch_position(current_username):
    '''
    Helper function
    Where are we in this batch of images?

    Takes:
    - string username
    Returns:
    - tuple: (current batch position, num images left in batch)
    '''

    me = "compute_batch_position()"

    # get user and current info
    current_entry = CurrentEntry.objects.get(jbid=current_username)
    current_reel = current_entry.reel
    current_image = current_entry.img
    current_position_in_reel = current_image.image_file.img_position
    num_images_in_reel = current_reel.image_count

    adapter.info(
        f"{me}: current_position_in_reel is {current_position_in_reel}",
        {'user': current_username}
    )

    # figure out batch size, handling corner case where batch_size > # images left in reel
    # case 1: # images in reel is evenly divisible by batch size, easy
    if num_images_in_reel % BATCH_SIZE == 0:
        batch_size = BATCH_SIZE

        adapter.info(
            f'{me}: case 1: batch_size is {batch_size}',
            {'user': current_username}
        )

    # case 2: # images not evenly divisible by batch size, need to compute final batch size and figure out where we are relative to end of the reel
    else:
        num_standard_batches = num_images_in_reel // BATCH_SIZE

        adapter.info(
            f'{me}: case 2',
            {'user': current_username}
        )

        if current_position_in_reel >= BATCH_SIZE * num_standard_batches:
            batch_size = num_images_in_reel % BATCH_SIZE + 1 # otherwise off by one error
            adapter.info(
                f'{me}: case 2B: batch_size is {batch_size}',
                {'user': current_username}
            ) 
        else:
            batch_size = BATCH_SIZE
            adapter.info(
                f'{me}: case 2A: batch_size is {batch_size}',
                {'user': current_username}
            ) 

    # modular arithmetic to compute where we are in a batch    
    current_batch_position = current_position_in_reel % batch_size
    num_images_left = batch_size - current_batch_position

    adapter.info(
        f"{me}: current_batch_position is {current_batch_position}, num_left is {num_images_left}, batch_size is {batch_size}", #, batch_done is {batch_done}
        {'user': current_username}
    )

    return current_batch_position, num_images_left, batch_size #, batch_done


def get_next_image(request):
    '''
    Helper function
    Look up next image for user to enter and put it in CurrentEntry
    '''

    # declare variables
    current_user = None
    current_username = None
    todo_image_qs = None

    # get user
    current_user = request.user
    current_username = current_user.username

    # get user to-do image lists
    todo_image_qs = get_image_todo_qs( request )
    todo_image_count = todo_image_qs.count()
    next_image = todo_image_qs.first()

    adapter.info(
        f'get_next_image got {next_image}',
        user=current_username
    )

    if next_image:

        current = CurrentEntry.objects.get(jbid=request.user)
        next_image_file = next_image.image_file
        current.img = next_image
        current.image_file = next_image_file
        current.save()

#-- END function get_next_image() --#


def get_request_data( request_IN ):

    '''
    Accepts django request.  Based on method, grabs the container for incoming
        parameters and returns it:
        - for method "POST", returns request_IN.POST
        - for method "GET", returns request_IN.GET
    '''

    # return reference
    request_data_OUT = None

    # do we have input parameters?
    if ( request_IN.method == 'POST' ):

        request_data_OUT = request_IN.POST

    elif ( request_IN.method == 'GET' ):

        request_data_OUT = request_IN.GET
        
    #-- END check to see request type so we initialize form correctly. --#

    return request_data_OUT

#-- END function get_request_data() --#


def get_image_todo_qs( request ):

    '''
    Helper function for IndexView
    Looks up current reel info and associated image queryset 

    Takes:
    - request
    Returns:
    - queryset of images to complete
    '''

    # return reference
    qs_OUT = None

    # declare variables
    current_user = None
    current_username = None
    user_image_qs = None
    todo_image_qs = None

    # get user
    current_user = request.user
    current_username = current_user.username

    # get list of images in this reel 
    current_reel = CurrentEntry.objects.get(jbid = current_username).reel
    reel_image_qs = Image.objects.filter(image_file__img_reel = current_reel)
    user_image_qs = reel_image_qs.filter(jbid = current_username)
    todo_image_qs = user_image_qs.filter( is_complete = False )

    # order according to ImageFile name instead of id in case loaded wrong?
    todo_image_qs = todo_image_qs.order_by("image_file__img_position")

    adapter.info(
        f'get_image_todo_qs() reel_image_qs length {len(reel_image_qs)}, todo_image_qs length {len(todo_image_qs)}',
        user = current_username
    )

    qs_OUT = todo_image_qs

    return qs_OUT

#-- END function get_next_image() --#


def initialize_context( request_IN, dict_IN = None ):

    '''
    Accepts request, optional context dictionary. If no dictionary passed in,
        makes a new one. Does standard initialization, returns initialized
        dictionary.
    '''

    # return reference
    dict_OUT = None

    # declare variables
    current = None

    # set context to what is passed in.
    dict_OUT = dict_IN

    # got anything?
    if ( dict_OUT is None ):

        # no. Make new dictionary.
        dict_OUT = {}

    #-- END check if dictionary passed in. --#

    # CSRF
    dict_OUT.update( csrf( request_IN ) )

    # param names
    dict_OUT[ CONTEXT_PARAM_NAMES ] = PARAM_NAMES

    # retrieve things from current
    current = CurrentEntry.objects.get( jbid = request_IN.user )
    dict_OUT[ CONTEXT_BREAKER_INSTANCE ] = current.breaker
    dict_OUT[ CONTEXT_USERNAME ] = request_IN.user.username 

    return dict_OUT

#-- END function initialize_context() --#


def assign_reel(keyer):
    '''
    Helper method for IndexView to assign a keyer the images from a given reel
     by loading image info into Image model for a keyer. In other words, when
     this method is called, it creates a row for each image in the assigned
     reel for the given keyer.

    Required arguments:
    - keyer 
    Returns: 
    - assigned reel object or None (if no reels left for this keyer)
    '''

    me = 'assign_reel()'
    this_reel = None

    # - take the ones that have 0 or 1 keyer assigned
    # - exclude the 1990 dummy breaker reel
    # - exclude ones already assigned to this keyer
    reel_qs = Reel.objects.filter(keyer_count__lt = 2)
    reel_qs = reel_qs.exclude(reel_name = 'dummy_breaker_reel')
    reel_qs = reel_qs.exclude(Q(keyer_one = keyer) | Q(keyer_two = keyer))

    # do we have any reels to assign?
    if len(reel_qs) == 0:
        adapter.info(
            f'{me}: found no reels to assign',
            user = keyer.jbid
        )
        return None

    # prefer to assign reels that have 0 keyers over those that have 1
    # then assign reels with lower IDs (i.e. those loaded earlier) over higher
    # take the one at the top
    ordered_reel_qs = reel_qs.order_by('keyer_count', 'id')
    adapter.info(
        f'reel queue is {list(ordered_reel_qs)}'
    )
    this_reel = ordered_reel_qs[0]
 
    # set the keyer
    if this_reel.keyer_one is None:
        this_reel.keyer_one = keyer

    elif this_reel.keyer_two is None:
        this_reel.keyer_two = keyer

    else:
        adapter.warn(
            f'assign_images() reel has a keyer issue /n keyer one is {this_reel.keyer_one} keyer two is {this_reel.keyer_two}',
            user = keyer.jbid
        )
        raise ValueError

    # increment reel keyer count
    this_reel.keyer_count += 1
    this_reel.save()

    # also increment keyer reel count
    keyer.reel_count += 1
    keyer.save()

    # now, get year and associated image files 
    year = this_reel.year
    image_file_qs = ImageFile.objects.filter(img_reel_id = this_reel)

    # loop through and create Image instance w/this keyer 
    for image_file_instance in image_file_qs:

        img = Image( 
                image_file=image_file_instance, \
                jbid=keyer.jbid, \
                is_complete=False, \
                year=year,
                image_type=None, \
                problem=False
            )
        img.save()


    #-- END loop over images in the reel --#

    return this_reel

#-- END function assign_reel() --#


def seed_current_entry(request):

    '''
    Helper function for IndexView: Put dummy data into current entry
     table. It should only be called for the first image for each user.
    '''

    # declare variables
    current_qs = None
    current_count = None
    this_image = None
    this_breaker = None
    current = None

    adapter.info(
        f'seed_current_entry() call \n {request}',
        user = request.user.username
    )

    # got a current for current user?
    current_qs = CurrentEntry.objects.filter(jbid=request.user)
    current_count = current_qs.count()
    this_keyer = Keyer.objects.get(jbid=request.user)

    # if this user doesn't have a row in CurrentEntry, we need to do stuff
    if ( current_count == 0 ):

        # does this keyer have any reels assigned?
        reel_qs = Reel.objects.filter(Q(keyer_one = this_keyer) | Q(keyer_two = this_keyer))

        # if not, assign a reel
        if reel_qs.count() == 0:
            this_reel = assign_reel(this_keyer)
        
        # if so, go get one of those reels
        # prioritize reels that were loaded first...? 
        else:
            this_reel = reel_qs.order_by('id')[0]
        

        first_imagefile = ImageFile.objects.filter(img_reel = this_reel)[0]
        # first_imagefile = this_reel.imagefile_set.get_queryset() #TODO test this out
        first_image = Image.objects.get(
            jbid = this_keyer.jbid,
            image_file = first_imagefile
        )
        
        #  populate Current Entry
        current = CurrentEntry(
            keyer = this_keyer,
            jbid = this_keyer.jbid,
            reel = this_reel,
            image_file = first_imagefile,
            img = first_image,
        )
        current.save()



    #-- END check to see if we need to create current for new user. --#

#-- END function seed_current_entry() --#


def analyze_timing_list(timing_list_IN, label_IN = None, add_to_series_IN = True ):

    # return reference
    duration_list_OUT = None

    # declare variables
    status_message = None
    work_duration = None
    duration_sum = None
    duration_list = None
    index_1 = None
    index_2 = None
    time_1 = None
    time_2 = None
    percent_of_total_duration = None

    # init
    duration_list = []

    # Initial label
    status_message = "\n\nTiming overview"
    if ( ( label_IN is not None ) and ( label_IN != "" ) ):
        status_message = "{header} ( {label} )".format(
            header = status_message,
            label = label_IN
        )
    #-- END check if label --#
    status_message += ":"
    print( status_message )

    # loop over items
    for timing_index in range( 0, ( len( timing_list_IN ) - 1 ) ):

        # time slice indices
        index_1 = timing_index
        index_2 = timing_index + 1

        # timestamps
        time_1 = timing_list_IN[ index_1 ][1]
        time_2 = timing_list_IN[ index_2 ][1]

        # get duration of current time slice.
        work_duration = time_2 - time_1

        # add to list of durations.
        duration_list.append( work_duration )

        # update sum.
        if ( duration_sum is None ):
            duration_sum = work_duration
        else:
            duration_sum = duration_sum + work_duration
        #-- END check if sum already has something in it --#

    #-- END loop over time slices --#

    # add to duration series?
    # if ( add_to_series_IN == True ):

    #     # yes.
    #     cls.api_profile_durations_series.append( duration_list )

    #-- END check to see if add to series --#

    # loop over durations for analysis
    for timing_index in range( 0, ( len( duration_list ) ) ):

        # time slice indices
        index_1 = timing_index
        index_2 = timing_index + 1

        # timestamps
        time_1 = timing_list_IN[ index_1 ]
        time_2 = timing_list_IN[ index_2 ]

        # get duration of current time slice.
        work_duration = duration_list[ index_1 ]

        # try percentage of total duration...
        percent_of_total_duration = work_duration / duration_sum

        # print time slice details
        status_message = "- {index} - {work_duration} - %: {percentage} ( {time_1} to {time_2} )".format(
            index = timing_index,
            work_duration = work_duration,
            percentage = percent_of_total_duration,
            time_1 = time_1,
            time_2 = time_2
        )
        print( status_message )

    #-- END loop over durations. --#

    # print total duration
    status_message = "- total: {duration_sum}".format( duration_sum = duration_sum )
    print( status_message )
    print( "\n\n" )

    duration_list_OUT = duration_list

    return duration_list_OUT

#-- END classmethod analyze_timing_list() --#


#==============================================================================#
# views
#==============================================================================#

#------------------------------------------------------------------------------#
# IndexView
#------------------------------------------------------------------------------#

class IndexView(LoginRequiredMixin, TemplateView):
    """
    Define view for app landing page
    """

    # some view-specific constants
    recent_image_limit = 5
    template_name = "EntryApp:index"


    def action_load_next_batch(self, current_username, context_IN):
        '''
        Modifies context dict to load new "fake" batch of images for keyers.
            - set num_completed images to 0
            - set num_images to min of batch_size and # images left in reel
            - compute num remaining
            - set recent_image_list to empty
        Takes: 
            - context dict
        Returns:
            - modified context dict
        '''

        me = 'IndexView:action_load_next_batch()'
        context_OUT = context_IN
        
        # now we reset the pointer in current entry too
        current_entry = CurrentEntry.objects.get(jbid=current_username)
        current_entry.batch_position = 0
        current_entry.save()

        context_OUT[ 'make_next_batch_button_appear' ] = False

        return context_OUT


    def action_load_next_reel(self, current_username):
        '''
        Helper method to put next reel in queue for a keyer. It is called from
        IndexView.process_request(). It populates CurrentEntry with a new reel
        when a keyer clicks the button. 

        - marks the existing reel in CurrentEntry (if there is one) complete
        for that keyer
        - queries DB for a new reel for that keyer
        - saves that reel in CurrentEntry for that keyer
        - returns boolean: True if we're out of reels, False otherwise
        '''

        me = 'IndexView.get_next_reel()'
        current = CurrentEntry.objects.get(jbid = current_username)
        this_keyer = Keyer.objects.get(jbid = current_username)

        adapter.info(
            f"{me}: loading new reel",
            user = current_username
        )

        # is there a reel in CurrentEntry? mark complete if so
        if current.reel:

            old_reel = current.reel

            adapter.info(
                f"{me}: replacing {old_reel}",
                user = current_username
            )
            
            # which keyer is this? mark old reel complete
            # handle case where first slot is null because we meddled
            if old_reel.keyer_one and old_reel.keyer_one.jbid == current_username:     
                old_reel.is_complete_keyer_one = True
                old_reel.save()
            
            elif old_reel.keyer_two.jbid == current_username:
                old_reel.is_complete_keyer_two = True
                old_reel.save()

            else:
                adapter.exception(
                    f"{me}: user is not assigned to either keyer slot in this reel",
                    user = current_username
                )
                raise ValueError

        # if not, assign the reel:
        #   priority goes to reels with one other keyer assigned
        #   then to reels with lower IDs 
        this_reel = assign_reel(this_keyer)

        # this is what happens if we got a new reel to assign
        # boolean seems backwards but it should be False
        if this_reel:

            # then update CurrentEntry
            current.reel = this_reel
            current.save()        
            return False
        
        # handle case where we're out of reels
        else: 

            return True


    def get(self, request):

        # return reference
        response_OUT = None

        adapter.info(
            'IndexView GET request',
            {'user': request.user.username}
        )

        # render response
        response_OUT = self.process_request( request )

        return response_OUT

    #-- END method get() --#


    def post(self, request):

        # return reference
        response_OUT = None

        adapter.info(
            'IndexView POST request',
            {'user': request.user.username}
        )

        # render response
        response_OUT = self.process_request( request )

        # reload page with get request, and proceed
        return response_OUT

    #-- END method post() --#


    def prepare_recent_image_queue(self, user_image_qs):
        '''
        Helper method to get most recent images: 
        - completed images with a year and a type, but not 1990 breakers
        - order images based on most recently modified to least recently modified
        - limited to recent_image limit (defined in process_request)
        '''
        me = "IndexView:prepare_recent_image_queue()"

        recent_image_qs = user_image_qs.filter( Q( year__isnull = False ) | Q( image_type__isnull = False ) )
        recent_image_qs = recent_image_qs.filter(is_complete = True)
        recent_image_qs = recent_image_qs.exclude( (Q(year__exact = 1990) & Q(image_type__contains = 'breaker'))) # exclude 1900 dummy breaker
        recent_image_qs = recent_image_qs.order_by( '-last_modified' )
        recent_image_qs = recent_image_qs[ : self.recent_image_limit ]

        adapter.info(
            f'{me}: recent_image_qs is {recent_image_qs}'
        )

        return list( recent_image_qs )
        

    def process_request( self, request ):

        # return reference
        response_OUT = None

        # declare variables - config log
        me = "IndexView.process_request"
        adapter = CustomAdapter(logger, {'user': request.user.username})

        # declare variables
        # batch_size = None
        current_user = None
        current_username = None
        user_image_qs = None
        todo_image_qs = None
        todo_image_count = None
        recent_image_qs = None
        # recent_image_limit = None
        completed_image_qs = None
        completed_count = None
        next_image = None

        request_inputs = get_request_data(request)

        adapter.info(
            f'{me} request_inputs is {request_inputs}',
            {'user': request.user.username}
        )

        # # for profiling
        # timestamps_list = []
        # timestamps_list.append(('before any db queries', datetime.datetime.now()))

        # init state 
        seed_current_entry( request ) # ensures there's a value in CurrentEntry
        get_next_image( request ) # gets the next image loaded into CurrentEntry
        
        # prep context dict
        context = initialize_context( request ) 
        context[ 'app_instance' ] = settings.APP_INSTANCE
        context[ 'make_next_batch_button_appear' ] = None
        context[ 'make_next_reel_button_appear' ] = None

        # get current username and current entry
        current_user = request.user
        current_username = current_user.username
        context[ "user" ] = current_user
        current_entry = CurrentEntry.objects.get(jbid = current_username)

        # get user image queryset for this reel and get recent images
        current_reel = current_entry.reel
        image_qs = Image.objects.filter(image_file__img_reel = current_reel)
        user_image_qs = image_qs.filter(jbid = current_username)
        recent_image_qs = self.prepare_recent_image_queue(user_image_qs)
        context[ 'recent_image_list' ] = recent_image_qs

        adapter.info(
            f'{me}: current reel is {current_reel}',
            {'user': current_username}
        )

        # get queue of images to code and add next image to context for thumbnail
        todo_image_qs = get_image_todo_qs( request )
        todo_image_ct = todo_image_qs.count()
        next_image = todo_image_qs.first()
        context[ "todo_image_count" ] = todo_image_ct
        context[ 'next_image' ] = next_image

        # timestamps_list.append(('after todo_image_qs before context stuff', datetime.datetime.now()))

        # get batch information for keyers
        if next_image:

            current_batch_position, images_left_in_batch, batch_size = compute_batch_position(current_username)

            # if batch_position == 0, we're at the end of a batch but haven't entered data yet
            if current_batch_position == 0: 
                
                current_batch_position = batch_size
                images_left_in_batch = batch_size - current_batch_position # should always be 0
                batch_done = False
                
                # set up button to appear when we finish this image
                current_entry.batch_position = 1 # change to bool later
                current_entry.save()

                adapter.info(
                    f'{me}: case 3A',
                    {'user': current_username}
                ) 

                
            # if batch_position == 1 and we have the batch flag, then we want the button
            elif current_batch_position == 1 and current_entry.batch_position == 1:
                # current_batch_position = batch_size
                batch_done = True

                adapter.info(
                    f'{me}: case 3B',
                    {'user': current_username}
                ) 

            # we're in the middle of a batch and everything's easy
            else:

                batch_done = False

                adapter.info(
                    f'{me}: case 3C',
                    {'user': current_username}
                )         

            # now that we've made adjustments, set context variables
            context[ 'num_completed' ] = current_batch_position
            context[ 'num_images' ] = batch_size
            context[ 'num_todo' ] = images_left_in_batch

        else:
            context[ 'num_completed' ] = None
            context[ 'num_images' ] = None
            context[ 'num_todo' ] = None


        # timestamps_list.append(('after context stuff before sketchy action section', datetime.datetime.now()))
        # check if all images in reel or batch are completed
        # if so, reveal one of two buttons
        # - advance to next reel if more images needed (takes priority)
        # - advance to "new batch" if batch_position is zero
        completed_count = user_image_qs.filter( is_complete = True ).count()

        adapter.info(
            f'{me}(): completed_count is {completed_count}',
            {'user': current_username}
        )
        adapter.info(
            f'{me}(): current_reel.image_count is {current_reel.image_count}',
            {'user': current_username}
        )

        if completed_count == current_reel.image_count:
            # this will reveal a button that has backend effects
            context[ 'make_next_reel_button_appear' ] = True
            adapter.info(f'{context}')
        
        # this case will reveal a button that has no backend effects but will
        # allow user to trigger reset of count of images to do
        elif batch_done:
            context[ 'make_next_batch_button_appear' ] = True


        # do we have an action? if so, do action
        action = request_inputs.get( PARAM_NAME_ACTION, None)

        adapter.info(
            f'{me} action is {action}',
            {'user': current_username}
        )

        if action == ACTION_LOAD_NEXT_REEL:

            adapter.info(
                f'{me} got action: {action}',
                {'user': current_username}
            )

            # load new reel: out_of_reels is a boolean indicating if reel load worked
            # if it didn't, it's probably because we're out of reels for that keyer 
            out_of_reels = self.action_load_next_reel(current_username)
            context[ 'out_of_reels' ] = out_of_reels

        elif action == ACTION_LOAD_NEXT_BATCH:

            adapter.info(
                f'{me} got action: {action}',
                {'user': current_username}
            )

            context = self.action_load_next_batch(current_username, context)

        # got an action but not one in defined list, this is an error
        elif action and action not in INDEX_ACTIONS:

            adapter.exception(
                f'{me}() unknown POST action',
                {'user': request.user.username}
            )


        adapter.info(
            f"{me}(): context[num_completed] is {context['num_completed']}",
            {'user': current_username}
        )

        # render response
        context["popOut"] = True if request_inputs.get("popOut") else False
        response_OUT = render( request, 'EntryApp/index.html', context )

        # timestamps_list.append(('after sketchy action button section, last one', datetime.datetime.now()))

        # adapter.info(
        #     analyze_timing_list(timestamps_list),
        #     # timestamps_list,
        #     {'user': 'profiler'}
        # )


        return response_OUT

    #-- END method process_request() --#


#-- END view class IndexView

#------------------------------------------------------------------------------#
# CodeImage
#------------------------------------------------------------------------------#

class CodeImage( LoginRequiredMixin, FormView ):

    '''
    # Processing:

    - action = view, image, type, record

        - if action = view, populate forms, no changes.
        - if action = image, retrieve information from image form, use it to update image.

            - if image already has breaker or sheet, don't allow type to be updated.
 
        - if action = type, retrieve type, then based on type, retrieve information from type form and update breaker or sheet.

    # Template cells:

    - display image.
    - image info

        - if image_id, load data, pre-populate form from
        - if image already has breaker or sheet, don't allow type to be updated.

    - edit based on type

        - if no type, do not output cell.
        - if image_type, try to retrieve record for type appropriate for image.
        - if found, prepopulate form.
        - render form

    - if breaker, list out sheets with edit button for each.

    - if sheet, then, edit records

        - if type is not sheet, do not output.
        - if record ID, load into edit form, if not, empty form.
        - output list of records, sorted by index. Beside each, output edit form.
    '''

    # form class variables
    form_image = ImageForm
    template_name = 'EntryApp/code-image.html'

    def action_complete_image( self, request_IN, context_IN ):
        '''
        Marks an image as "complete" from button 
        Only applies to sheets - happens to breakers automatically 
        '''
        
        me = "CodeImage.action_complete_sheet"
        error_message = None
        error_list_OUT = None

        # check for request
        if request_IN:

            inputs_IN = get_request_data(request_IN)
            form = inputs_IN
            
            image_id = form.get( PARAM_NAME_IMAGE_ID, None )

            
            # check for image ID
            if image_id:

                # if we get one, mark as complete
                image_instance = Image.objects.get(pk = image_id)
                image_instance.is_complete = True
                image_instance.save()

                # also increment the pointer in CurrentEntry
                make_batch_done_true(request_IN.user.username)
            
            else:

                adapter.info(
                    f"{me}(): no image id",
                    {'user': request_IN.user.username}
                )
                # no inputs?
                error_message = "In {method}(): No image ID received ( {form} ).".format(
                    method = me,
                    form = form
                )
                error_list_OUT.append( error_message )

        return error_list_OUT


    def action_update_breaker( self, request_IN, context_IN ):

        '''
        Accepts form inputs. Updates breaker from inputs.
        '''

        # return reference
        error_list_OUT = None

        # declare variables
        me = "CodeImage.action_update_breaker"
        error_message = None
        error_list = None
        current = None
        inputs_IN = None
        image_id = None
        image_instance = None
        image_has_related_objects = None
        form = None
        field_query = None
        breaker_fields = None
        BreakerFormSet = None
        BreakerFormSetHelper = None
        formset = None
        cleaned_data = None
        cleaned_data_count = None
        breaker_id = None
        breaker_qs = None
        breaker_count = None
        breaker_instance = None
        breaker_data = None
        is_changed = None
        temp_breaker_instance = None

        # init
        error_list_OUT = list()

        # got request?
        if ( request_IN is not None ):

            # get inputs
            inputs_IN = get_request_data( request_IN )

            # get current reel for year and state info
            current = CurrentEntry.objects.get(jbid = request_IN.user.username)
            current_reel = Reel.objects.get(id = current.reel_id)

            # get image for ID 
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )

            if image_id:
                image_instance = Image.objects.get( pk = image_id )
                image_has_related_objects = image_instance.has_related_objects()
            else:
                adapter.exception(
                    f'{me}(): no image ID in inputs_IN',
                    {'user': request_IN.user.username}
                )

            form = inputs_IN
            
            adapter.info(
                f'{me}(): Breaker form is {form}',
                {'user': request_IN.user.username}
            )

            # define fields based on which year it is
            breaker_fields = get_form_fields(image_instance.year, "breaker")

            BreakerFormSet = modelformset_factory( 
                Breaker,
                fields = breaker_fields,
                formset = BaseBreakerFormSet 
            )
            formset = BreakerFormSet( inputs_IN, request_IN.FILES )
            helper = BreakerFormHelper(year=image_instance.year)

            adapter.info(
                f"{me}(): breaker formset is {formset}"
            )

            # get data from request
            try:
                if formset.is_valid():
                    cleaned_data = formset.cleaned_data
                    cleaned_data_count = len( cleaned_data )

                else:
                    adapter.warn(f"Formset is not valid. I don't know why!")

            # maybe triggered when data is submitted without required fields?
            except AttributeError as e:

                adapter.error(
                    f"AttributeError in action_update_breaker. No cleaned_data in formset? {e}",
                    {'user': request_IN.user.username}
                )                

                error_message = "In {method}: problem getting data out of the form. Are all required fields filled out?".format(
                    method = me,
                )
                error_list_OUT.append(error_message)
                
                cleaned_data_count = -1 # do this to skip rest of logic


            # do we have just 1?
            if ( cleaned_data_count == 1 ):

                # prepare data to use to create/update Breaker.
                breaker_data = formset.cleaned_data[0]
                breaker_data['img'] = image_instance
                breaker_data['jbid'] = request_IN.user.username
                breaker_data['timestamp'] = datetime.datetime.now()
                breaker_data['state'] = current_reel.state
                breaker_data['year'] = current_reel.year

                # remove "id" since it breaks qs.update().
                if ( "id" in breaker_data ):

                    # id is there - remove it (we are already filtering on pk to make sure we update correct instance).
                    temp_breaker_instance = breaker_data.pop( "id" )

                #-- END check to see if ID in breaker data. --#

                #error_message = "breaker_data: {}".format( breaker_data )
                #error_list_OUT.append( error_message )

                # do we have a breaker ID?
                breaker_id = form.get( PARAM_NAME_BREAKER_ID, None )
                if ( ( breaker_id is not None ) and ( breaker_id != "" ) ):

                    # try to get breaker, to update.
                    Breaker.objects.filter( pk = breaker_id ).update( **breaker_data )

                    # update
                    breaker_qs = Breaker.objects.filter( pk = breaker_id )

                    # get instance
                    breaker_instance = breaker_qs.get()

                else:

                    # no ID. New breaker.
                    breaker_instance = Breaker.objects.create( **breaker_data )

                    # is it time to set Image to complete?
                    image_instance.is_complete = True
                    image_instance.save()

                    # new breaker - update CurrentEntry with breaker and batch position
                    current = CurrentEntry.objects.get( jbid = request_IN.user )
                    current.breaker = breaker_instance
                    current.save()

                    # increment batch position
                    make_batch_done_true(request_IN.user.username)

                #-- END check to see if new or existing --#

            else:

                # no inputs?
                error_message = "In {method}(): Data received for multiple Breaker records ( {breaker_data} ). What is going on?".format(
                    method = me,
                    breaker_data = breaker_data
                )
                error_list_OUT.append( error_message )

            #-- END check to see if more than one set of data passed in. --#

            # return the breaker instance in context?
            context_IN[ CONTEXT_BREAKER_INSTANCE ] = breaker_instance
            context_IN[ CONTEXT_BREAKER_FORM_HELPER ] = helper

        else:

            # no inputs?
            error_message = "In {method}(): No inputs passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_breaker() --#


    def action_update_image( self, request_IN, context_IN ):

        '''
        Accepts form inputs. Looks for image form inputs. If found, checks to
            make sure the image can be updated (if it has a related sheet or a
            related breaker instance, should not be updated?)
        '''

        # return reference
        error_list_OUT = None

        # declare variables
        me = "CodeImage.action_update_image"
        error_message = None
        error_list = None
        inputs_IN = None
        image_id = None
        image_instance = None
        image_has_related_objects = None
        year_value = None
        image_type_value = None
        is_changed = None

        # init
        error_list_OUT = list()

        # got request?
        if ( request_IN is not None ):

            # get inputs.
            inputs_IN = get_request_data( request_IN )

            # get image for ID
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )
            image_has_related_objects = image_instance.has_related_objects()

            logger.info(
                f"{me}(): image has related? {image_has_related_objects}",
                {'user': request_IN.user.username}
            )

            # Only allow updates if image doesn't already have related.
            if ( image_has_related_objects == False ):

                # get image info from form inputs.

                # year
                year_value = inputs_IN.get( PARAM_NAME_YEAR, None )

                logger.info(
                    f"{me}(): {image_id} and {year_value}",
                    {'user': request_IN.user.username}
                )

                # got a value?
                if ( ( year_value is not None ) and ( year_value != "" ) ):

                    # different?
                    year_value = int( year_value )
                    if ( year_value != image_instance.year ):

                        # changed value!

                        # update
                        image_instance.year = year_value
                        is_changed = True

                    #-- END check to see if changed value --#

                #-- END check if year passed in. --#

                # type
                image_type_value = inputs_IN.get( PARAM_NAME_IMAGE_TYPE, None )

                # got a value?
                if ( ( image_type_value is not None ) and ( image_type_value != "" ) ):

                    # different?
                    if ( image_type_value != image_instance.image_type ):

                        # changed value!

                        # update
                        image_instance.image_type = image_type_value
                        is_changed = True

                    #-- END check to see if changed value --#

                #-- END check if year passed in. --#

                # any changes?
                if ( is_changed == True ):

                    # yes - save.
                    image_instance.save()

                #-- END check to see if changes. --#

            else:

                # image has related instances - can't update, need to ask for help.
                error_message = "In {method}(): Image {me} has related breaker or sheet, so can't update this way. Please ask for help updating this image.".format(
                    method = me,
                    me = self
                )
                error_list_OUT.append( error_message )

            #-- END check to see if image has related instances. --#

        else:

            # no inputs?
            error_message = "In {method}(): No request passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_image() --#


    def action_update_longform( self, request_IN, context_IN ):

        '''
        Accepts form inputs. Updates longform from inputs.
        '''

        # return reference
        error_list_OUT = None

        # inits
        me = "CodeImage.action_update_longform"
        error_message = None
        error_list = None
        inputs_IN = None
        current = None
        image_id = None
        image_instance = None
        image_has_related_objects = None
        associated_breaker = None
        form = None
        field_query = None
        longform_id = None
        longform_qs = None
        longform_count = None
        longform_instance = None
        longform_data = None
        longform_defaults = None
        is_changed = None
        is_new_longform = False

        # init
        error_list_OUT = list()
        

        # got request?
        if ( request_IN is not None ):

            # get inputs
            inputs_IN = get_request_data( request_IN )

            # get image for ID
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )

            form = inputs_IN

            adapter.info(
                f'{me}(): LongForm1990 inputs_IN is {form}',
                {'user': request_IN.user.username}
            )

            # do we have a longform ID?
            longform_id = form.get( PARAM_NAME_LONGFORM_ID, None )

            adapter.info(
                f'{me}(): longform_id is {longform_id}',
                {'user': request_IN.user.username}
            )

            if longform_id:

                # try to get instance to update.
                longform_qs = LongForm1990.objects.filter( pk = longform_id )

                # get instance
                longform_instance = longform_qs.get()


                adapter.info(
                    f'{me}(): longform_instance is {longform_instance}',
                    {'user': request_IN.user.username}
                )

            else:

                # no ID. New long form.
                longform_instance = LongForm1990()

        #-- END check to see if new or existing --#

            # define fields based on which year it is
            fields = get_form_fields(1990, 'long') 
            field_widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}

            # TODO: what should this condition actually check for?                
            if form:


                # collect data that we're entering for this longform
                l_data = {f: form[f] for f in form if f in fields}
                adapter.info(
                    f'{me}(): longform form collected data is {l_data}',
                    {'user': request_IN.user.username}
                )
                    
                # add additional fields
                l_data['img'] = image_instance
                l_data['jbid'] = request_IN.user.username
                l_data['last_modified'] = datetime.datetime.now()

                # if the request passed in an instance, we do an update
                if longform_id:
                    adapter.info(
                        f"{me}(): got longform_id {longform_id}",
                        {'user': request_IN.user.username}
                    )

                    # get the existing longform record and update it 
                    try:
                        with transaction.atomic():
                            LongForm1990.objects.filter(pk=longform_id).update(**l_data)
                    
                    except IntegrityError as e:

                        # check the underlying reason
                        cause = e.__cause__

                        adapter.warning(
                            f"{me}(): IntegrityError in action_update_sheet, {cause}",
                            {'user': request_IN.user.username}
                        )

                        # this probably means they double clicked or the app is slow
                        if 'unique_1990LF_entry' in str(cause):

                            error_message = "In {method}(): longform image already exists. If you are stuck and can't enter data, please go back to the home page and resume coding this image from there.".format( method = me )
                            error_list_OUT.append( error_message )
            
                        else:

                            error_message = "In {method}(): Uncaught error. Please make a Teams post to alert us to the issue.".format( method = me )
                            error_list_OUT.append( error_message )    

                    # get the instance
                    longform_instance = LongForm1990.objects.filter(pk=longform_id).get()
                    
                # no ID => new longform record
                else:
                    adapter.info(
                        f"{me}(): no longform_id, creating new object",
                        {'user': request_IN.user.username}
                    )

                    try:
                        with transaction.atomic():
                            longform_instance = LongForm1990.objects.create(**l_data)

                    except Exception as e:

                        cause = e.__cause__

                        adapter.warning(
                            f"{me}(): Exception in action_update {cause}",
                            {'user': request_IN.user.username}
                        )

                        if 'unique_1990LF_entry' in str(cause):

                            error_message = "In {method}(): longform image already exists. If you are stuck and can't enter data, please go back to the home page and resume coding this image from there.".format( method = me )
                            error_list_OUT.append( error_message )

                        else:

                            error_message = "In {method}(): Uncaught error. Please make a Teams post to alert us to the issue.".format( method = me )
                            error_list_OUT.append( error_message )

                    # increment current batch position
                    # make_batch_done_true(request_IN.user.username)

                    #-- END check to see if this is a longform create or update--#
                
            else:

                error_message = "In {method}(): Form data was invalid ({form})".format(method = me, form = form)

            #-- END check to see if there was more than one record passed in --#

            # return the sheet instance in context?
            context_IN[ CONTEXT_LONGFORM_INSTANCE ] = longform_instance

        else:

            # no inputs?
            error_message = "In {method}(): No inputs passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_longform() --#


    def action_update_other_image( self, request_IN, context_IN ):

        '''
        Accepts form inputs. Looks for inputs from OtherImage form. If found, 
        tries to update values.
        '''

        # return reference
        error_list_OUT = None

        # declare variables
        me = "CodeImage.action_update_other_image"
        error_message = None
        error_list = None
        inputs_IN = None
        image_id = None
        image_instance = None

        # init
        error_list_OUT = list()

        # got request?
        if ( request_IN is not None ):

            # get inputs.
            inputs_IN = get_request_data( request_IN )

            # get image for ID
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )

            # do we have an image ID?
            other_image_id = inputs_IN.get( PARAM_NAME_OTHER_IMAGE_ID, None )
    
            # update if so
            if other_image_id:
    
                adapter.info(
                    f"{me}(): got OtherImage id, updating description",
                    {'user': request_IN.user.username}
                )

                other_image_instance = OtherImage.objects.get(pk = other_image_id)

                other_image_instance.description = inputs_IN['description']

                try:
                    with transaction.atomic():
                        other_image_instance.save()
                    
                except IntegrityError as e:
                    
                    cause = e.__cause__

                    adapter.warning(
                        f"{me}(): IntegrityError in action_update_sheet, {cause}",
                        {'user': request_IN.user.username}
                    )

                    if 'unique_other_entry' in str(cause):

                        error_message = "In {method}(): other image already exists. If you are stuck and can't enter data, please go back to the home page and resume coding this image from there.".format( method = me )
                        error_list_OUT.append( error_message )
            
                    else:

                        error_message = "In {method}(): Uncaught error. Please make a Teams post to alert us to the issue.".format( method = me )
                        error_list_OUT.append( error_message )    
    
            # otherwise create one
            else: 
                                
                adapter.info(
                    f"{me}(): no OtherImage id, creating new instance",
                    {'user': request_IN.user.username}
                )

                ot_data = {}
                ot_data['img'] = image_instance
                ot_data['jbid'] = request_IN.user
                ot_data['year'] = image_instance.year
                ot_data['description'] = inputs_IN['description']
                

                try:                
                    with transaction.atomic():
                        other_image_instance = OtherImage.objects.create(**ot_data) 

                        # set Image to complete after initial creation
                        image_instance.is_complete = True
                        image_instance.save()

                except Exception as e:

                    cause = e.__cause__

                    adapter.warning(
                        f"{me}(): Exception in action_update {cause}",
                        {'user': request_IN.user.username}
                    )

                    if 'unique_other_entry' in str(cause):

                        error_message = "In {method}(): other image already exists. If you are stuck and can't enter data, please go back to the home page and resume coding this image from there.".format( method = me )
                        error_list_OUT.append( error_message )

                    else:

                        error_message = "In {method}(): Uncaught error. Please make a Teams post to alert us to the issue.".format( method = me )
                        error_list_OUT.append( error_message )


                # increment current batch position
                make_batch_done_true(request_IN.user.username)

            #-- END check to see if other image ID present --#

        else:

            # no inputs?
            error_message = "In {method}(): No request passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_other_image() --#


    def action_edit_record( self, request_IN, context_IN ):
        '''
        Action to re-populate form blankly
        '''

        # mini-init
        me = "CodeImageView.action_edit_record"
        error_list_OUT = list()
        formset = None
        helper = None
        record_instance = None

        # got request?
        if ( request_IN is not None ):

            # get inputs
            inputs_IN = get_request_data( request_IN )

            # removed stuff here

        else:

            # no inputs?
            error_message = "In {method}(): No inputs passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_edit_record() --#


    def action_update_record( self, request_IN, context_IN ):
        '''
        Accepts form inputs. Updates record from those inputs.
        '''

        # mini-init
        me = "CodeImageView.action_update_record"
        error_list_OUT = list()
        formset = None
        helper = None
        record_instance = None

        # got request?
        if ( request_IN is not None ):

            # get inputs
            inputs_IN = get_request_data( request_IN )

            # get image for ID 
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )

            # get sheet 
            sheet_id = inputs_IN.get( PARAM_NAME_SHEET_ID, None )
            sheet_instance = Sheet.objects.get( pk = sheet_id )

            # get record_id from kform, if there is one
            record_id = inputs_IN.get(PARAM_NAME_RECORD_ID, None)

            form = inputs_IN
            adapter.info(
                f'{me}: form is {form}',
                {'user': request_IN.user.username}
            )

            # check that there's a sheet ID passed in
            if sheet_instance:

                # define fields based on which year it is
                record_fields = get_form_fields(image_instance.year, 'short') #TODO: should not be hardcoded?

                # TODO: what should this condition actually check for?                
                if form:

                    # collect data that we're entering for this record
                    r_data = {f: form[f] for f in form if f in record_fields}
                        
                    # add additional fields
                    r_data['sheet'] = sheet_instance
                    r_data['jbid'] = request_IN.user.username
                    r_data['timestamp'] = datetime.datetime.now()
                    r_data['is_complete'] = True

                    adapter.info(
                        f'{me}(): record form cleaned_data is {r_data}',
                        {'user': request_IN.user.username}
                    )

                    # if the request passed in a record, we do an update
                    if record_id:
                        adapter.info(
                            f"{me}(): got record_id {record_id}",
                            {'user': request_IN.user.username}
                        )

                        # get the record and update it 
                        Record.objects.filter(pk=record_id).update(**r_data)

                        # get the instance
                        record_instance = Record.objects.filter(pk=record_id).get()
                    
                    # no ID => new record
                    else:
                        adapter.info(
                            f"{me}(): no record_id, creating new object",
                            {'user': request_IN.user.username}
                        )
                        record_instance = Record.objects.create(**r_data)

                    #-- END check to see if this is a record create or update--#
                
                else:

                    error_message = "In {method}(): Form data was invalid ({form})".format(method = me, form = form)

                #-- END check to see if there was more than one record passed in --#
                 
            else:

                logger.warning("{me}: no sheet instance passed in context".format(me = me))

        
        else:

            # no inputs?
            error_message = "In {method}(): No inputs passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_record() --#


    def action_update_sheet( self, request_IN, context_IN ):

        '''
        Accepts form inputs. Updates sheet from inputs.
        '''

        # return reference
        error_list_OUT = None

        # declare variables
        me = "CodeImage.action_update_sheet"
        error_message = None
        error_list = None
        inputs_IN = None
        current = None
        image_id = None
        image_instance = None
        image_has_related_objects = None
        associated_breaker = None
        form = None
        field_query = None
        sheet_id = None
        sheet_qs = None
        sheet_count = None
        sheet_instance = None
        sheet_data = None
        sheet_defaults = None
        is_changed = None
        is_new_sheet = None

        # init
        error_list_OUT = list()
        is_new_sheet = False

        # got request?
        if ( request_IN is not None ):

            # get inputs
            inputs_IN = get_request_data( request_IN )

            # get image for ID
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )
            image_has_related_objects = image_instance.has_related_objects()

            form = inputs_IN

            adapter.info(
                f'Sheet form is{form}',
                {'user': request_IN.user.username}
            )

            # 1990 never has breakers, so assign the default dummy
            if image_instance.year == 1990:
                # this breaker gets created for each user during data loading
                # associated_breaker = Breaker.objects.filter(year=1990).get(jbid=request_IN.user)

                dummy_reel = Reel.objects.get(reel_name='dummy_breaker_reel')
                dummy_breaker_imagefile = ImageFile.objects.get(img_reel_id=dummy_reel.id)
                dummy_breaker_image = Image.objects.filter(jbid=request_IN.user).get(image_file_id=dummy_breaker_imagefile.id)
                associated_breaker = Breaker.objects.get(img_id = dummy_breaker_image.id)

            else:
                associated_breaker = CurrentEntry.objects.get(jbid=request_IN.user).breaker
            #-- END figure out breaker based on year --#

            # get values from the form
            sheet_fields = get_form_fields(image_instance.year, 'sheet')
            sheet_data = {f: form[f] for f in form if f in sheet_fields}

            # turn checkbox value into a boolean because it isn't for some reason
            if image_instance.year == 1960:
                if sheet_data.get('hard_to_read', False):
                    sheet_data['hard_to_read'] = True
                else:
                    sheet_data['hard_to_read'] = False


            # add additional values
            sheet_data['img'] = image_instance
            sheet_data['year'] = image_instance.year 
            sheet_data['jbid'] = request_IN.user.username
            sheet_data['timestamp'] = datetime.datetime.now()
            sheet_data['breaker'] = associated_breaker            

            # do we have a sheet ID?
            sheet_id = form.get( PARAM_NAME_SHEET_ID, None )

            # if we have a sheet ID, try an update
            if ( ( sheet_id is not None ) and ( sheet_id != "" ) ):

                try:
                    with transaction.atomic():
                        Sheet.objects.filter(id=sheet_id).update(**sheet_data)

                except IntegrityError as e:

                    # check the underlying reason
                    cause = e.__cause__

                    adapter.warning(
                        f"{me}(): IntegrityError in action_update_sheet, {cause}",
                        {'user': request_IN.user.username}
                    )

                    # this probably means there's no breaker associated with the 
                    # sheet. need to check this out by hand
                    if 'null value in column "breaker_id" violates not-null constraint' in str(cause):

                        # we want to exit here gracefully, don't update CurrentEntry
                        error_message = "In {method}(): This sheet doesn't have a breaker associated with it. You will not be able to proceed with keying records. Please make a Teams post to alert us to the issue.".format( method = me )
                        error_list_OUT.append( error_message )                

                    else:

                        error_message = "In {method}(): Uncaught error. Please make a Teams post to alert us to the issue.".format( method = me )
                        error_list_OUT.append( error_message )    

                # regardless, do not update "CurrentEntry" on update.
                is_new_sheet = False

            else:

                # no ID. New sheet.
                try:
                    with transaction.atomic():
                        sheet_instance = Sheet.objects.create(**sheet_data)

                except IntegrityError as e:

                    # check the underlying reason
                    cause = e.__cause__

                    adapter.warning(
                        f"{me}(): IntegrityError in action_update_sheet, {cause}",
                        {'user': request_IN.user.username}
                    )

                    # this constraint is violated if they click multiple times on 
                    # the page without sheet ID in context
                    if 'unique_sheet_entry' in str(cause):

                        # we want to exit here gracefully, don't update CurrentEntry
                        error_message = "In {method}(): sheet already exists. If the record entry block did not appear, please go back to the home page and resume coding this image from there.".format( method = me )
                        error_list_OUT.append( error_message )                

                    # this probably means there's no breaker associated with the 
                    # sheet. need to check this out by hand
                    elif 'null value in column "breaker_id" violates not-null constraint' in str(cause):

                        # we want to exit here gracefully, don't update CurrentEntry
                        error_message = "In {method}(): This sheet doesn't have a breaker associated with it. You will not be able to proceed with keying records. Please make a Teams post to alert us to the issue.".format( method = me )
                        error_list_OUT.append( error_message )                

                    else:
                        
                        error_message = "In {method}(): Uncaught error. Please make a Teams post to alert us to the issue.".format( method = me )
                        error_list_OUT.append( error_message )    

                # regardless, do not update "CurrentEntry" on update.
                is_new_sheet = False

            #-- END check to see if new or existing --#

            # new sheet?
            if ( is_new_sheet == True ):

                # new sheet - update CurrentEntryfor convenience. 
                current = CurrentEntry.objects.get( jbid = request_IN.user )
                current.sheet = sheet_instance
                current.save()

            #-- END check if new sheet. --#

            # return the sheet instance in context?
            context_IN[ CONTEXT_SHEET_INSTANCE ] = sheet_instance


        else:

            # no inputs?
            error_message = "In {method}(): No inputs passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_sheet() --#


    def get( self, request ):

        # return reference
        response_OUT = None

        adapter.info(
            'CodeImageView GET request',
            {'user': request.user.username}
        )

        # render response
        response_OUT = self.process_request( request )
        return response_OUT

    #-- END method get() --#

    def post( self, request ):

        # return reference
        response_OUT = None

        adapter.info(
            'CodeImageView POST request',
            {'user': request.user.username}
        )

        # render response
        response_OUT = self.process_request( request )

        return response_OUT

    #-- END method post() --#


    def prepare_breaker_context( self, image_IN, context_IN ):

        # return reference
        context_OUT = None

        # declare variables
        me = 'CodeImage.prepare_breaker_context'
        breaker_qs = None
        breaker_count = None
        my_breaker = None
        field_qs = None
        breaker_fields = None
        BreakerFormSet = None
        formset_extra_count = None

        # init
        formset_extra_count = 0

        # add on to context passed in.
        context_OUT = context_IN

        # if breaker:
        # - look up breaker instance for this image (could be None).
        # - render breaker form, populated if there is already a breaker
        #     instance for this image.
        # - pull in images, link to edit each, OR link to edit next image.

        # is there an existing Breaker instance?
        breaker_qs = image_IN.breaker_set.all()
        breaker_count = breaker_qs.count()

        # do we have a breaker?
        if ( breaker_count == 1 ):

            # yes, one match - get instance
            my_breaker = breaker_qs.get()

            # set up form so it displays current, doesn't output extra.
            formset_extra_count = 0

        elif ( breaker_count == 0 ):

            # no instance yet...
            my_breaker = None

            # set up form so it displays 1 empty.
            formset_extra_count = 1

        elif ( breaker_count > 1 ):

            # multiple? how to pick? Don't...
            my_breaker = None

            # set up formset so it doesn't have extra (will output all)
            formset_extra_count = 0

            # log error message.
            adapter.error(
                "Multiple breakers for image {image}. Not good.".format( image = image_IN ),
                {'user': "_"}
            )

        #-- END check if single breaker. --#

        context_OUT[ CONTEXT_BREAKER_INSTANCE ] = my_breaker

        # set up form.
        field_qs = FormField.objects.filter( year = image_IN.year )
        field_qs = field_qs.filter( form_type = "breaker" )
        logger.info( f'{me}: FormField query length was {len(field_qs)}' )
        breaker_fields = [f.field_name for f in list(field_qs)]

        BreakerFormSet = modelformset_factory(
            Breaker,
            fields = breaker_fields,
            formset = BaseBreakerFormSet,
            extra = formset_extra_count
        )
        formset = BreakerFormSet( queryset = breaker_qs )
        helper = BreakerFormHelper(year = image_IN.year)
        

        context_OUT[ CONTEXT_BREAKER_FORMSET ] = formset
        context_OUT[ CONTEXT_BREAKER_FORM_HELPER ] = helper

        return context_OUT

    #-- END method prepare_breaker_context() --#


    def prepare_image_context( self, image_IN, context_IN ):

        me = "CodeImageView.prepare_image_context()"

        # return reference
        context_OUT = None

        # declare variables
        image_has_related_objects = None
        image_form_values = None
        image_form = None

        # add on to context passed in.
        context_OUT = context_IN

        # send image info to template.
        context_OUT[ "img" ] = image_IN
        context_OUT[ "reel_name" ] = image_IN.image_file.img_reel.reel_name
        context_OUT[ "slug" ] = image_IN.image_file.smaller_image_file_name

        # does image have related objects?
        image_has_related_objects = image_IN.has_related_objects()

        # does image have related objects?
        if ( image_has_related_objects == False ):

            # no - OK to still make the fields editable...?
            # populate forms from database for existing rows.
            image_form_values = dict()
            image_form_values[ PARAM_NAME_YEAR ] = image_IN.year
            image_form_values[ PARAM_NAME_IMAGE_TYPE ] = image_IN.image_type

            # look up reel name
            username = context_IN[ CONTEXT_USERNAME ]
            current = CurrentEntry.objects.get(jbid = username)
            reel_name = current.reel.reel_name 

            # create image form(s).
            # note we do want reel_name here because this is how we check for long form 1990
            image_form = ImageForm( image_IN.year, reel_name, image_form_values )

            # send them to template.
            context_OUT[ "image_form" ] = image_form

        else:

            # no form
            context_OUT[ "image_form" ] = None

        #-- END check if image has related objects, only editable if not --#

        return context_OUT

    #-- END method prepare_image_context() --#


    def prepare_longform_context( self, image_IN, context_IN ):

        me = 'CodeImageView.prepare_longform_context'

        # inits
        context_OUT = context_IN
        longform_instance = None

        # look up existing instance for this image
        longform_qs = image_IN.longform1990_set.all()

        # there shouldn't be more than one
        if longform_qs.count() == 1:
            longform_instance = longform_qs.get()
        elif longform_qs.count() > 1:
            adapter.error(
                f"Multiple 1990 long forms associated with image {image_IN}.",
                {'user': "_"}
            )

        context_OUT[ CONTEXT_LONGFORM_INSTANCE ] = longform_instance

        # define fields based on which year it is
        fields = get_form_fields(1990, 'long') 
        field_widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}

        # - render form, populated if there is already a longform
        #     instance for this image.
        LongForm1990Form = modelform_factory(LongForm1990, fields=fields, widgets = field_widgets)
        helper = LongFormHelper(year='1990')

        if longform_instance:
            this_form = LongForm1990Form(instance = longform_instance)

        else:
            this_form = LongForm1990Form()

        context_OUT[ CONTEXT_LONGFORM_FORM ] = this_form
        context_OUT[ CONTEXT_LONGFORM_HELPER ] = helper

        adapter.info(
            f'{me}: context_OUT is {context_OUT}',
            {'user': "_"}
        )

        return context_OUT


    def prepare_other_image_context( self, image_IN, context_IN ):
        
        me = 'CodeImageView.prepare_other_image_context'

        # inits
        context_OUT = context_IN
        this_other_image = None

        # look up existing instance for this image
        other_image_qs = image_IN.otherimage_set.all()

        adapter.info(
            f"{me}(): other_image_qs is {other_image_qs}",
            {'user': "_"}
        )

        # there shouldn't be more than one
        if other_image_qs.count() == 1:
            this_other_image = other_image_qs.get()
        elif other_image_qs.count() > 1:
            adapter.error(
                f"Multiple OtherImages associated with image {image_IN}.",
                {'user': "_"}
            )

        adapter.info(
            f"{me}(): this_other_image is {this_other_image}",
            {'user': "_"}
        )

        context_OUT[ CONTEXT_OTHER_IMAGE_INSTANCE ] = this_other_image

        # - render form, populated if there is already an OtherImage
        #     instance for this image.
        this_form = OtherImageForm( instance =  this_other_image )

        context_OUT[ CONTEXT_OTHER_IMAGE_FORM ] = this_form

        adapter.info(
            f'{me}: context_OUT is {context_OUT}',
            {'user': "_"}
        )

        return context_OUT


    def prepare_record_context( self, image_IN, context_IN, request_inputs):

        me = 'CodeImageView.prepare_record_context'

        # add on to context passed in
        context_OUT = context_IN

        # look up parent sheet instance (relying on Jon's error check in prepare_sheet_context)
        parent_sheet = image_IN.sheet_set.get()  

        # look up associated record(s) and sort in order of keyed row/column
        # line_no is filled in for 1960/1970; col_no for 1980/1990, but whichever
        # is null will be null for all records on sheet -> does not affect sort
        record_qs = parent_sheet.record_set.all().order_by('line_no', 'col_no')
        record_count = record_qs.count()

        # DEBUG
        adapter.info(
            f'{me}: record_count is {record_count}',
            {'user': "_"}
        )
        adapter.info(
            f'{me}: context_IN is {context_IN}',
            {'user': "_"}
        )

        # set up form.
        record_fields = get_form_fields( parent_sheet.year, 'short' ) #TODO: THIS SHOULD NOT BE HARD-CODED
        field_widgets = {f: choices.FORM_WIDGETS[f] for f in record_fields if f in choices.FORM_WIDGETS}

        RecordForm = modelform_factory(Record, fields = record_fields, widgets = field_widgets)
        helper = RecordFormHelper(year=parent_sheet.year)

        # get the action from context
        my_action = request_inputs.get(PARAM_NAME_ACTION, None)
        record_id = request_inputs.get(PARAM_NAME_RECORD_ID, None)

        adapter.info(
            f'prepare_record_context my_action is {my_action}',
            {'user': "_"}
        )


        if CONTEXT_RECORD_INSTANCE in context_IN.keys():
            record_instance = context_IN[ CONTEXT_RECORD_INSTANCE ]

        elif my_action == ACTION_EDIT_RECORD:
            record_instance = Record.objects.get(id=record_id)            

        else:
            record_instance = None

        adapter.info(
            f"{me}(): record_instance has id {record_id}, {record_instance}",
            {'user': "_"}
        )

        # did we get a record id?
        if record_instance and my_action == ACTION_EDIT_RECORD:

            # yes, this is where we render the form for editing, so all
            # edit form work goes here and stays inside this conditional
            form = RecordForm(instance = record_instance)
            context_OUT[ CONTEXT_RECORD_INSTANCE ] = record_instance
    
        else:
            form = RecordForm()

        context_OUT[ CONTEXT_RECORD_FORM ] = form
        context_OUT[ CONTEXT_RECORD_FORMSET_HELPER ] = helper
        context_OUT[ CONTEXT_RECORD_LIST ] = record_qs


        adapter.info(
            f'context returned from prepare_record_context {context_OUT}',
            {'user': "_"}
        )

        return context_OUT

    #-- END method prepare_record_context() --#


    def prepare_sheet_context( self, image_IN, context_IN, request_inputs ):

        # return reference
        context_OUT = None

        # declare variables
        me = 'CodeImage.prepare_sheet_context'
        sheet_qs = None
        sheet_count = None
        sheet_instance = None
        this_form = None
        this_year = image_IN.year

        # add on to context passed in.
        context_OUT = context_IN

        adapter.info(
            f"{me}() for image {image_IN}",
            {'user': request_inputs.get('username', None)}
        )


        # - look up sheet instance for this image (could be None).
        # is there an existing Sheet instance?
        sheet_qs = image_IN.sheet_set.all()
        sheet_count = sheet_qs.count()

        if ( sheet_count == 1 ):
            sheet_instance = sheet_qs.get()
        elif ( sheet_count > 1 ):
            adapter.error( 
                "Multiple sheets for image {image}. Not good.".format( image = image_IN ),
                {'user': "_"}
            )
        #-- END check if single sheet. --#

        context_OUT[ CONTEXT_SHEET_INSTANCE ] = sheet_instance

        # look up fields
        fields = get_form_fields(this_year, 'sheet')
        widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}

        # set up form
        SheetForm = modelform_factory(Sheet, fields=fields, widgets=widgets)
        helper = SheetFormHelper(year=this_year)

        # - if sheet instance:
        #     - render Sheet form, prepopulated with current Sheet info
        #     - render record form, prepopulate if record ID is present.
        #     - pull in records, sorted by row ID, and then output list with
        #         edit link next to each.
        if sheet_instance:

            form = SheetForm(instance = sheet_instance) 

            context_OUT = self.prepare_record_context( image_IN, context_OUT, request_inputs )

        else:

            form = SheetForm()

        context_OUT[ CONTEXT_SHEET_FORM ] = form
        context_OUT[ CONTEXT_SHEET_HELPER ] = helper

        return context_OUT

    #-- END method prepare_sheet_context() --#


    def process_action( self, request_IN, context_IN ):

        # return reference
        error_list_OUT = None

        # declare variables
        me = "CodeImage.process_action"
        error_message = None
        error_list = None
        request = None
        request_inputs = None
        current_user = None
        current_username = None
        request_inputs = None
        current_image_id = None
        current_action = None
        image_qs = None
        current_image = None
        context = None
        my_action = None
        action_error_list = None

        # init
        context = initialize_context( request_IN )
        error_list = list()
        request = request_IN

        # got request?
        if ( request_IN is not None ):

            # get request inputs (get or post)
            request_inputs = get_request_data( request_IN )

            # get IDs of image to process.
            current_image_id = request_inputs.get( PARAM_NAME_IMAGE_ID, None )

            # do we have an image ID?
            if ( ( current_image_id is not None ) and ( current_image_id != "" ) ):

                # is there an action?
                my_action = request_inputs.get( PARAM_NAME_ACTION, None )
                if ( ( my_action is not None ) and ( my_action in VALID_ACTIONS ) ):

                    # what action?
                    action_error_list = None
                    adapter.info(
                        f'CodeImageView.process_action() action is {my_action}',
                        {'user': "_"}
                    )
                    
                    if ( my_action == ACTION_COMPLETE_IMAGE ):
                        
                        # mark image as complete
                        action_error_list = self.action_complete_image( request_IN, context_IN ) 

                    elif ( my_action == ACTION_EDIT_RECORD ):
                        
                        # edit the record (from the table of entered records)
                        action_error_list = self.action_edit_record( request_IN, context_IN ) 
                    
                    elif ( my_action == ACTION_UPDATE_IMAGE ):

                        # update the image
                        action_error_list = self.action_update_image( request_IN, context_IN )

                    elif ( my_action == ACTION_UPDATE_BREAKER_TYPE ):

                        # update the breaker
                        action_error_list = self.action_update_breaker( request_IN, context_IN )

                    elif ( my_action == ACTION_UPDATE_LONGFORM ):

                        # update the 1990 longform
                        action_error_list = self.action_update_longform( request_IN, context_IN )

                    elif ( my_action == ACTION_UPDATE_OTHER_IMAGE ):

                        # update the OtherImage
                        action_error_list = self.action_update_other_image( request_IN, context_IN )

                    elif ( my_action == ACTION_UPDATE_RECORD ):

                        # update the record
                        action_error_list = self.action_update_record( request_IN, context_IN )

                    elif ( my_action == ACTION_UPDATE_SHEET_TYPE ):

                        # update the sheet
                        action_error_list = self.action_update_sheet( request_IN, context_IN )

                    else:

                        # known but unsupported action. Error?
                        error_message = "Action {requested_action} is known ( VALID_ACTIONS: {action_list} ) but not implemented.".format(
                            requested_action = my_action,
                            action_list = VALID_ACTIONS
                        )
                        error_list.append( error_message )

                    #-- END check to see which action --#

                    # action errors?
                    if ( ( action_error_list is not None ) and ( len( action_error_list ) > 0 ) ):

                        # append action errors to list.
                        error_list.extend( action_error_list )

                    #-- END check to see if action errors. --#

                else:

                    #-- unknown action - error. --#
                    error_message = "Action {requested_action} is unknown ( VALID_ACTIONS: {action_list} ). No action processed.".format(
                        requested_action = my_action,
                        action_list = VALID_ACTIONS
                    )
                    error_list.append( error_message )

                #-- END check to see if known action --#

            else:

                # no image ID. Error. can not proceed.
                error_message = "No image ID found in request, can't code image."
                error_list.append( error_message )

            #-- END check to see if image ID passed in. --#

        else:

            # no request?
            error_message = "In {method}(): No request passed in, can't process.".format(
                method = me
            )
            error_list.append( error_message )

        #-- END check to see if request passed in. --#

        # errors?
        if ( len( error_list ) > 0 ):

            # store it.
            error_list_OUT = error_list

        #-- END check for error list --#

        return error_list_OUT

    #-- END method process_action() --#


    def process_request( self, request ):

        # return reference
        response_OUT = None

        # config logger
        me = "CodeImage.process_request"

        # declare variables
        error_message = None
        error_list = None
        request_inputs = None
        current_user = None
        current_username = None
        request_inputs = None
        current_image_id = None
        current_action = None
        image_qs = None
        current_image = None
        image_has_related_objects = None
        context = None
        my_action = None
        got_action = None
        returned_error_list = None

        # declare variables - image forms
        image_has_related_objects = None
        image_form_values = None
        image_year_form = None
        image_type_form = None

        # declare variables - image type
        current_image_type = None

        # init  
        return_template_name = self.template_name
        context = initialize_context( request )
        error_list = list()

        # get request inputs (get or post)
        request_inputs = get_request_data( request )
        # if you need request_inputs in a prepare_context method, pass request_inputs in
        # please don't mess with the context

        # get current user info
        current_user = request.user.username
        context[ "user" ] = current_user

        adapter.info(
            f'CodeImageView.process_request(): request_inputs are {request_inputs}',
            {'user': current_user}
        )

        # get IDs of image to process.
        current_image_id = request_inputs.get( PARAM_NAME_IMAGE_ID, None )

        # do we have an image ID?
        if ( ( current_image_id is not None ) and ( current_image_id != "" ) ):

            # is there an action?
            my_action = request_inputs.get( PARAM_NAME_ACTION, None )
            
            adapter.info(
                f"{me}() my_action is {my_action}",
                {'user': current_user}
            )
            
            if ( ( my_action is not None ) and ( my_action in VALID_ACTIONS ) ):

                # process action
                got_action = True
                returned_error_list = self.process_action( request, context )
                if ( ( returned_error_list is not None ) and ( len( returned_error_list ) > 0 ) ):
                    error_list.extend( returned_error_list )
                #-- END check if process_action errors. --#

                # if the action is complete_image, update_breaker_type, update_other_image, we return to the index
                if my_action in [
                    ACTION_COMPLETE_IMAGE, \
                    ACTION_UPDATE_OTHER_IMAGE, \
                    ACTION_UPDATE_BREAKER_TYPE
                ]:
                    
                    popout = "popOut=true" if "popOut" in request_inputs else ""
                    return redirect("{}?{}".format(reverse("EntryApp:index"), popout))
                
                #-- END check to see if action is completing image --#

            #-- END check to see if action. --#

            #------------------------------------------------------------------#
            # ==> Image

            # retrieve image
            image_qs = Image.objects.filter( pk = current_image_id )
            current_image = image_qs.get()

            # prepare image context
            context = self.prepare_image_context( current_image, context )

            # what type?
            current_image_type = current_image.image_type

            # ==> breaker
            if ( current_image_type == choices.IMAGE_TYPE_BREAKER ):

                # prepare breaker context.
                context = self.prepare_breaker_context( current_image, context )

            # ==> 1990 long form
            elif ( current_image_type == choices.IMAGE_TYPE_LONGFORM ):
                
                # prepare longform context
                context = self.prepare_longform_context( current_image, context )

            # ==> sheet
            elif ( current_image_type == choices.IMAGE_TYPE_SHEET ):

                # prepare sheet context (which also prepares record context)
                context = self.prepare_sheet_context( current_image, context, request_inputs )
                # logger.info(f'CodeImage prepare_sheet_context context is {context}')

            elif ( current_image_type == choices.IMAGE_TYPE_OTHER ):

                # unknown image type. Ummm...
                context = self.prepare_other_image_context( current_image, context )

            elif ( ( current_image_type is None ) or ( current_image_type == "" ) ):

                # No image type.

                # does it have related objects? If so, error, if not, new image,
                #     proceed.
                image_has_related_objects = current_image.has_related_objects()
                if ( image_has_related_objects == True ):

                    # unknown image type. Ummm...
                    error_message = "No image type for image {me}, but it has related Breaker or Sheet. Error. Look in the admin for details. No further editing possible.".format(
                        image_type = current_image_type,
                        me = self
                    )
                    error_list.append( error_message )

                #-- END check if has related objects. --#

            else:

                # unknown image type. Ummm...
                error_message = "Unknown image type {image_type} for image {me}. No further editing possible.".format(
                    image_type = current_image_type,
                    me = self
                )
                error_list.append( error_message )

            #-- END check to see what type of image we have. --#

        else:

            # no image ID. Error. can not proceed.
            error_list.append( "No image ID found in request, can't code image." )

        #-- END check to see if image ID passed in. --#

        # errors?
        if ( ( error_list is not None ) and ( len( error_list ) > 0 ) ):

            # store it.
            context[ CONTEXT_PAGE_STATUS_MESSAGE_LIST ] = error_list

        #-- END check for error list --#

        state_x = request_inputs.get('state_x')
        state_y = request_inputs.get('state_y')
        state_zoom = request_inputs.get('state_zoom')
        popOut = request_inputs.get('popOut', 'false')
        context['image_state'] = {'x': state_x, 'y': state_y, 'zoom': state_zoom, 'popOut': popOut}
        response_OUT = render( request, return_template_name, context )

        return response_OUT

    #-- END method process_request() --#

#-- END class CodeImage --#

#------------------------------------------------------------------------------#
# PROBLEM VIEW
#------------------------------------------------------------------------------#

def parse_http_referral(url, username):
    '''
    Helper function for report_problem view
    Parses referring url from HTTP request to extract site of problem

    Takes: 
    - string from the HTTP request referring url
    - string username (for logging)
    Returns:
    - string name of model affected
    '''
    if url:
    
        page_name = re.search('(?<=EntryApp/).+/', url).group(0)[:-1]
    
        adapter.info(
            f"parse_http_referral: {page_name}",
            {'user': username}
        )
    
        return page_name
    
    else:

        adapter.info(
            f'parse_http_referral did not get a url, returning empty string.',
            {'user': username}
        )
        return ""


@login_required
def report_problem(request):
    '''
    View to render problem form so user can record an issue

    This is a functional view that can handle either GET or POST requests. It 
    will redirect to the index view after the user submits their form.
    '''

    current = CurrentEntry.objects.get(jbid=request.user)

    # get referring URL if present
    try:
        referring_url = request.META['HTTP_REFERER']
    except Exception:
        referring_url = ""

    flagged_view = parse_http_referral(referring_url, request.user.username)


    inputs_IN = get_request_data(request)
    adapter.info(f"inputs_IN is {inputs_IN}")

    # did we get image ID? 
    image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )

    if image_id:

        image_instance = Image.objects.get(pk=image_id)

        adapter.info(
            f'report_problem GET request for {image_id}',
            {'user': request.user.username}
        )
        adapter.info(
            f"report_problem referred from view {flagged_view} at {referring_url}",
            {'user': request.user.username}
        )

    else:
        
        image_instance = None
        adapter.info(
            f"report_problem GET request with no image id",
            {'user': request.user.username}
        )
        adapter.info(
            f"report_problem referred from view {flagged_view} and {referring_url}",
            {'user': request.user.username}
        )

            
    if request.method == "GET":

        return render(
                request, \
                'EntryApp/report-problem.html',
                {
                    'image_id': image_id,
                    'image': image_instance,
                    'form': ProblemForm(),
                    'reel_name': image_instance.image_file.img_reel.reel_name,
                    'slug': image_instance.image_file.smaller_image_file_name,
                    'year': image_instance.year
                }
            )

    elif request.method == "POST":

        adapter.info(f"report_problem: request.POST is {request.POST}")

        form = ProblemForm(inputs_IN)


        if form.is_valid():

            form_data = form.cleaned_data
            # adapter.info(f'form.is_valid() is {form.is_valid()}')
            # adapter.info(f'form.data is {form_data}')
            adapter.info(f'form.cleaned_data is {form.cleaned_data}')

            problem_image_id = image_id
            problem_image = image_instance

            adapter.info(
                f'report_problem POST request for file {problem_image.image_file.img_file_name}',
                {'user': request.user.username}
            )
            adapter.info(
                f'report_problem problem_image id is {problem_image.id}',
                {'user': request.user.username}
            )

            try:
            
                # get instance of problematic image
                problem_image = Image.objects.get(id = problem_image.id)

                # get the info out of the form
                is_problem = form_data.get('problem', False)
                prob_description = form_data.get('description', None)
                # is_problem = True if 'problem' in form.fields.keys() else False
                # prob_description = form.fields.get('description', None)

                adapter.info(f'is_problem is {is_problem}', {'user': ''})
                adapter.info(f'prob_description is {prob_description}', {'user': ''})

                with transaction.atomic():

                    # update image instance
                    problem_image.problem = is_problem
                    problem_image.prob_description = prob_description
                    problem_image.save()


                adapter.info(f'problem_image.problem is {problem_image.problem}')
                adapter.info(f'problem_image.prob_description is {problem_image.prob_description}')
                
                return redirect(reverse('EntryApp:index'))


            # if this raises an exception, we stay on this page with an empty problem form
            except Exception as e:

                adapter.error(
                    f"Exception in report_problem: ", 
                    {'user': request.user.username},
                    e
                )

                return render(
                    request, \
                    'EntryApp/report-problem.html',
                    {
                        'image': current.img,
                        'form': ProblemForm(),
                        'reel_name': current.reel.reel_name,
                        'slug': current.img.image_file.smaller_image_file_name,
                        'year': problem_image.year
                    }
            )

#------------------------------------------------------------------------------#
# AUTHENTICATION VIEWS
#------------------------------------------------------------------------------#

def login_user(request):
    '''
    View for logging users into the entry application
    '''
    pass


def logout_user(request):
    '''
    View for logging users out of the application
    '''
    pass

#------------------------------------------------------------------------------#
# EXAMPLE VIEWS
#------------------------------------------------------------------------------#

def test_crispy_formset_view(request, year, form_type):
    '''
    View for testing django crispy formsets
    '''

    adapter.info(
        f'test_crispy_formset_view() request: {request}',
        {'user': request.user.username}
    )

    fields = get_form_fields(year, form_type) 
    field_widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}
    
    adapter.info(
        f'crispy formset fields are {fields}',
        {'user': request.user.username}
    )


    # different layout helpers depending on form type
    if form_type == "short":

        TestCrispyForm = modelform_factory(
            Record,
            fields = fields,
            widgets = field_widgets
        )
        form = TestCrispyForm()
        helper = CrispyFormSetHelper(year=year)
    
    elif form_type == "long":

        TestCrispyForm = modelform_factory(
            LongForm1990,
            fields = fields,
            widgets = field_widgets
        )
        form = TestCrispyForm()
        helper = CrispyLongFormHelper(year=year)
    
    else:
        adapter.error(
            f"test_crispy_formset_view(): unknown form_type is {form_type}",
            {'user': request.user.username}
        )
        raise ValueError

    ft = ''
    if form_type == "long":
        ft = form_type + '_'

    context = {
        'year': year,
        'form_type': ft,
        'formset': form,
        'helper': helper
    }

    return render(request, 'EntryApp/test-crispy-formset.html', context)

    
def render_image(request):
    imgpath = request.GET["imgpath"]
    return render(request, 'EntryApp/render-image.html', {"imgpath": imgpath})

def test_household1960_form(request):
    '''
    Temporary view for developing the 1960 household form layout
    '''

    # set field order
    fields = [
        'address_one',
        'address_two',
        'sample_key_one',
        'sample_key_two',
        'sample_key_three',
        'sample_key_four',
        'house_number_one',
        'house_number_two',
        'house_number_three',
        'house_number_four',
        'apt_number_one',
        'apt_number_two',
        'apt_number_three',
        'apt_number_four',
    ]

    # set widgets
    field_widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}

    # initialize form and helper
    household_form = modelform_factory(
        Household1960,
        fields = fields,
        widgets = field_widgets
    )
    helper = Household1960FormHelper()
    
    context = {
        'household_form': household_form,
        'helper': helper
    }

    return render(request, 'EntryApp/develop-household1960.html', context)
