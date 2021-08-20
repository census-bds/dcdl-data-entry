"""
VIEWS FOR DCDL DATA ENTRY

TO DO:
-integrate openseadragon info into views
"""

# python imports
import datetime
import logging
import re


# django imports
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.db.models import Q
import django.forms as forms
from django.forms import formset_factory
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
from EntryApp.models import LongForm1990
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Reel
from EntryApp.models import Sheet

# EntryApp forms
from EntryApp.forms import BaseBreakerFormSet
from EntryApp.forms import BaseRecordFormSet
from EntryApp.forms import BreakerForm
from EntryApp.forms import CrispyFormSetHelper
from EntryApp.forms import ImageForm
from EntryApp.forms import ImageTypeForm
from EntryApp.forms import ImageYearForm
from EntryApp.forms import LongForm1990Form
from EntryApp.forms import LongFormHelper
from EntryApp.forms import OtherImageForm
from EntryApp.forms import ProblemForm
from EntryApp.forms import RecordForm
from EntryApp.forms import RecordFormHelper
from EntryApp.forms import SheetForm

# EntryApp choices
import EntryApp.choices as choices


#==============================================================================#
# CONSTANTS-ish
#==============================================================================#

# standard context names
CONTEXT_BREAKER_INSTANCE = "breaker_instance"
CONTEXT_BREAKER_FORMSET = "breaker_formset"
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
CONTEXT_RECORD_FORMSET_HELPER = "helper"
CONTEXT_RECORD_LIST = "record_list"
CONTEXT_SHEET_INSTANCE = "sheet_instance"
CONTEXT_SHEET_FORM = "sheet_form"

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

# actions
ACTION_COMPLETE_IMAGE = "complete_image"
ACTION_UPDATE_BREAKER_TYPE = "update_breaker_type"
ACTION_UPDATE_IMAGE = "update_image"
ACTION_UPDATE_LONGFORM = "update_longform"
ACTION_UPDATE_OTHER_IMAGE = "update_other_image"
ACTION_UPDATE_SHEET_TYPE = "update_sheet_type"
ACTION_UPDATE_RECORD = "update_record"
VALID_ACTIONS = []
VALID_ACTIONS.append( ACTION_COMPLETE_IMAGE )
VALID_ACTIONS.append( ACTION_UPDATE_BREAKER_TYPE )
VALID_ACTIONS.append( ACTION_UPDATE_IMAGE )
VALID_ACTIONS.append( ACTION_UPDATE_LONGFORM )
VALID_ACTIONS.append( ACTION_UPDATE_OTHER_IMAGE )
VALID_ACTIONS.append( ACTION_UPDATE_SHEET_TYPE )
VALID_ACTIONS.append( ACTION_UPDATE_RECORD )

#==============================================================================#
# variables
#==============================================================================#

logger = logging.getLogger('EntryApp.views')

#==============================================================================#
# functions
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
    allowed_forms = ['breaker', 'short', 'long']
    logger.info("get_form_fields got {year}, {form_type}".format(year=year, form_type=form_type))

    if year in allowed_years and form_type in allowed_forms:

        field_query = FormField.objects.filter(year=year).filter(form_type=form_type)
        logger.info(f'FormField query length was {len(field_query)}')
        return [f.field_name for f in list(field_query)]

    else:

        logger.info(f'Invalid argument for get_fields: {year} {form_type}')
        return []

def get_next_image(request):

    '''
    Helper function for BeginNewImageView
    Look up next image for user to enter and put it in CurrentEntry
    '''

    # declare variables
    current_user = None
    current_username = None
    todo_image_qs = None

    # get user
    current_user = request.user
    current_username = current_user.username

    # get user TODO image lists
    todo_image_qs = get_image_todo_qs( request )
    todo_image_count = todo_image_qs.count()
    next_image = todo_image_qs.first()

    logger.info(f'get_next_image got {next_image}')

    if next_image:
        current = CurrentEntry.objects.get(jbid=request.user)
        current.img = next_image
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
    Helper function for BeginNewImageView
    Look up next image for user to enter and put it in CurrentEntry
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

    # get user image lists
    # TODO: revise this so it's images left in this reel
    user_image_qs = Image.objects.filter( jbid = current_username )
    todo_image_qs = user_image_qs.filter( is_complete = False )
    # todo_image_qs = todo_image_qs.order_by( 'image_file__img_reel_label', 'image_file__img_reel_index', 'image_file__img_position', )

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

    return dict_OUT

#-- END function initialize_context() --#


def seed_current_entry(request):

    '''
    Helper function for BeginNewImageView: Put dummy data into current entry
     table. It should only be called for the first image for each user.
    '''

    # declare variables
    current_qs = None
    current_count = None
    an_image = None
    a_breaker = None
    current = None

    # got a current for current user?
    current_qs = CurrentEntry.objects.filter(jbid=request.user)
    current_count = current_qs.count()
    if ( current_count == 0 ):

        # these will be overwritten, I think, so values don't matter
        logger.info(f'seed_current_entry inserting into CurrentEntry')
        an_image = Image.objects.all()[0]
        a_breaker = Breaker.objects.create(jbid=request.user, img=an_image)
        current = CurrentEntry.objects.create(jbid=request.user, \
                                            img=an_image, \
                                            breaker = a_breaker, \
                                            sheet = None)
        a_breaker.delete() # delete temp breaker from Breaker model

    #-- END check to see if we need to create current for new user. --#

#-- END function seed_current_entry() --#


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

    def get(self, request):

        # return reference
        response_OUT = None

        # render response
        response_OUT = self.process_request( request )

        return response_OUT

    #-- END method get() --#

    def process_request( self, request ):

        # return reference
        response_OUT = None

        # declare variables - config
        me = "IndexView.process_request"
        recent_image_limit = None

        # declare variables
        current_user = None
        current_username = None
        user_image_qs = None
        total_image_count = None
        todo_image_qs = None
        todo_image_count = None
        recent_image_qs = None
        recent_image_list = None
        recent_image_count = None
        completed_image_qs = None
        completed_count = None
        next_image = None
        context = None

        # init
        recent_image_limit = 5
        seed_current_entry( request ) # this ensures there's a value in CurrentEntry
        get_next_image( request )
        context = initialize_context( request )


        # get current username
        logger.info(f'user info:\n \t {request.user}')
        current_user = request.user
        current_username = current_user.username
        context[ "user" ] = current_user

        # get user image lists
        user_image_qs = Image.objects.filter( jbid = current_username )
        total_image_count = user_image_qs.count()
        context[ 'num_images' ] = total_image_count

        # todo
        todo_image_qs = get_image_todo_qs( request )
        todo_image_count = todo_image_qs.count()
        next_image = todo_image_qs.first()
        context[ 'num_todo' ] = todo_image_count
        context[ 'next_image' ] = next_image

        # completed work
        completed_image_qs = user_image_qs.filter( is_complete = True )
        completed_image_qs = completed_image_qs.exclude( Q(year__exact = 1990) & Q(image_type__contains = 'breaker')) # exclude 1900 dummy breaker
        completed_image_qs = completed_image_qs.order_by( '-last_modified' )
        completed_count = completed_image_qs.count()
        context[ 'num_completed' ] = completed_count

        # recent work: completed images with a year and a type, but not 1990 breakers
        recent_image_qs = user_image_qs.filter( Q( year__isnull = False ) | Q( image_type__isnull = False ) )
        recent_image_qs = recent_image_qs.filter(is_complete = True)
        recent_image_qs = recent_image_qs.exclude( Q(year__exact = 1990) & Q(image_type__contains = 'breaker')) # exclude 1900 dummy breaker
        recent_image_qs = recent_image_qs.order_by( '-last_modified' )
        recent_image_count = recent_image_qs.count()
        context[ 'num_in_progress' ] = recent_image_count

        # limit to recent_image_limit, and add list to context.
        recent_image_qs = recent_image_qs[ : recent_image_limit ]
        recent_image_list = list( recent_image_qs )
        context[ 'recent_image_list' ] = recent_image_list

        # render response
        response_OUT = render( request, 'EntryApp/index.html', context )

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
            
            else:

                logger.info(f"{me}(): no image id")
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

            # get image for ID (TODO: check for image ID)
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )
            image_has_related_objects = image_instance.has_related_objects()

            form = inputs_IN
            logger.info(f'Breaker form is{form}')

            # define fields based on which year it is
            breaker_fields = get_form_fields(image_instance.year, "breaker")

            BreakerFormSet = modelformset_factory( Breaker, fields = breaker_fields, formset = BaseBreakerFormSet )
            formset = BreakerFormSet( inputs_IN, request_IN.FILES )

            # get data from request
            cleaned_data = formset.cleaned_data
            cleaned_data_count = len( cleaned_data )

            logger.info(f'Breaker formset clean data should have length 1: {cleaned_data}')

            # do we have just 1?
            if ( cleaned_data_count == 1 ):

                # prepare data to use to create/update Breaker.
                breaker_data = formset.cleaned_data[0]
                breaker_data['img'] = image_instance
                breaker_data['year'] = image_instance.year
                breaker_data['jbid'] = request_IN.user.username
                breaker_data['timestamp'] = datetime.datetime.now()

                # Example breaker_data contents:
                # breaker_data: {
                #     'state': 'md',
                #     'county': 'pg',
                #     'mcd': '1',
                #     'tract': '1',
                #     'place': '1',
                #     'smsa': '1',
                #     'enumeration_district': '1',
                #     'id': <Breaker: Breaker 24 - file ID: 46 - file path: fake_IMG_0.jpg - year: 1980 - type: breaker from morga424>,
                #     'img': <Image: 24 - file ID: 46 - file path: fake_IMG_0.jpg - year: 1980 - type: breaker>,
                #     'year': 1980,
                #     'jbid': <SimpleLazyObject: <User: morga424>>,
                #     'timestamp': datetime.datetime(2021, 4, 23, 11, 12, 51, 508171)
                # }

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

                    # new breaker - update CurrentEntry
                    current = CurrentEntry.objects.get( jbid = request_IN.user )
                    current.breaker = breaker_instance
                    current.save()

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

            logger.info(f"{me}(): image has related? {image_has_related_objects}")

            # Only allow updates if image doesn't already have related.
            if ( image_has_related_objects == False ):

                # get image info from form inputs.

                # year
                year_value = inputs_IN.get( PARAM_NAME_YEAR, None )

                logger.info(f"{me}(): {image_id} and {year_value}")

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
            image_has_related_objects = image_instance.has_related_objects()

            form = inputs_IN

            logger.info(f'{me}(): LongForm1990 inputs_IN is {form}')

            # do we have a longform ID?
            longform_id = form.get( PARAM_NAME_SHEET_ID, None )

            if longform_id:

                # try to get instance to update.
                longform_qs = LongForm1990.objects.filter( pk = longform_id )

                # get instance
                longform_instance = longform_qs.get()

                # do not update "CurrentEntry" on update.
                is_new_longform = False

            else:

                # no ID. New sheet.
                longform_instance = LongForm1990()
                is_new_longform = True

            #-- END check to see if new or existing --#

                # define fields based on which year it is
                fields = get_form_fields(1990, 'long') 
                field_widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}

                # TODO: what should this condition actually check for?                
                if form:

                    # collect data that we're entering for this longform
                    l_data = {f: form[f] for f in form if f in fields}
                    logger.info(f'{me}(): longform form collected data is {l_data}')
                        
                    # add additional fields
                    l_data['img'] = image_instance
                    l_data['jbid'] = request_IN.user.username
                    l_data['last_modified'] = datetime.datetime.now()

                    # if the request passed in an instance, we do an update
                    if longform_id:
                        logger.info(f"{me}(): got longform_id {longform_id}")

                        # get the existing longform record and update it 
                        LongForm1990.objects.filter(pk=longform_id).update(**l_data)

                        # get the instance
                        longform_instance = LongForm1990.objects.filter(pk=longform_id).get()
                    
                    # no ID => new longform record
                    else:
                        logger.info(f"{me}(): no longform_id, creating new object")
                        longform_instance = LongForm1990.objects.create(**l_data)

                        # set Image to complete after initial creation
                        image_instance.is_complete = True
                        image_instance.save()


                    #-- END check to see if this is a longform create or update--#
                
                else:

                    error_message = "In {method}(): Form data was invalid ({form})".format(method = me, form = form)

                #-- END check to see if there was more than one record passed in --#

            # new sheet? do I need to update CurrentEntry? Not sure
            if ( is_new_longform == True ):

                # # new sheet - update CurrentEntry
                # current = CurrentEntry.objects.get( jbid = request_IN.user )
                # current.sheet = sheet_instance
                # current.save()
                pass

            #-- END check if new sheet. --#

            # return the sheet instance in context?
            context_IN[ CONTEXT_SHEET_INSTANCE ] = longform_instance

            # TODO: is it time to set Image to complete? Not yet here - once
            #     all records are complete. Add "finished" flag to record form.

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
    
                logger.info(f"{me}(): got OtherImage id, updating description")

                other_image_instance = OtherImage.objects.get(pk = other_image_id)

                other_image_instance['description'] = inputs_IN['description']
                other_image_instance.save()
    
            # otherwise create one
            else: 
                                
                logger.info(f"{me}(): no OtherImage id, creating new instance")

                ot_data = {}
                ot_data['img'] = image_instance
                ot_data['jbid'] = request_IN.user
                ot_data['year'] = image_instance.year
                ot_data['description'] = inputs_IN['description']
                
                other_image_instance = OtherImage.objects.create(**ot_data) 

                # set Image to complete after initial creation
                image_instance.is_complete = True
                image_instance.save()

            #-- END check to see if other image ID present --#

        else:

            # no inputs?
            error_message = "In {method}(): No request passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_other_image() --#



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
            logger.info(f'{me}: form is {form}')

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

                    logger.info(f'{me}(): record form cleaned_data is {r_data}')

                    # if the request passed in a record, we do an update
                    if record_id:
                        logger.info(f"{me}(): got record_id {record_id}")

                        # get the record and update it 
                        Record.objects.filter(pk=record_id).update(**r_data)

                        # get the instance
                        record_instance = Record.objects.filter(pk=record_id).get()
                    
                    # no ID => new record
                    else:
                        logger.info(f"{me}(): no record_id, creating new object")
                        record_instance = Record.objects.create(**r_data)

                    #-- END check to see if this is a record create or update--#
                
                else:

                    error_message = "In {method}(): Form data was invalid ({form})".format(method = me, form = form)

                #-- END check to see if there was more than one record passed in --#
                 
            else:

                logger.warning("{me}: no sheet instance passed in context".format(me = me))

            # return the record form instance + layout helper in context?
            context_IN[ CONTEXT_RECORD_INSTANCE ] = record_instance
            

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

            logger.info(f'Sheet form is{form}')

            # 1990 never has breakers, so assign the default dummy
            if image_instance.year == 1990:
                # this breaker gets created for each user during data loading
                associated_breaker = Breaker.objects.filter(year=1990).get(jbid=request_IN.user)
            else:
                associated_breaker = CurrentEntry.objects.get(jbid=request_IN.user).breaker
            #-- END figure out breaker based on year --#

            # do we have a sheet ID?
            sheet_id = form.get( PARAM_NAME_SHEET_ID, None )

            if ( ( sheet_id is not None ) and ( sheet_id != "" ) ):

                # try to get sheet, to update.
                sheet_qs = Sheet.objects.filter( pk = sheet_id )

                # get instance
                sheet_instance = sheet_qs.get()

                # do not update "CurrentEntry" on update.
                is_new_sheet = False

            else:

                # no ID. New sheet.
                sheet_instance = Sheet()
                is_new_sheet = True

            #-- END check to see if new or existing --#

            # set values and save.
            sheet_instance.img = image_instance
            sheet_instance.year = image_instance.year # should do this for all images and sheets automatically
            sheet_instance.jbid = request_IN.user.username
            sheet_instance.timestamp = datetime.datetime.now()
            sheet_instance.breaker = associated_breaker
            sheet_instance.num_records = form.get( 'num_records', None )
            sheet_instance.save()

            # new sheet?
            if ( is_new_sheet == True ):

                # new sheet - update CurrentEntry
                current = CurrentEntry.objects.get( jbid = request_IN.user )
                current.sheet = sheet_instance
                current.save()

            #-- END check if new sheet. --#

            # return the sheet instance in context?
            context_IN[ CONTEXT_SHEET_INSTANCE ] = sheet_instance

            # TODO: is it time to set Image to complete? Not yet here - once
            #     all records are complete. Add "finished" flag to record form.

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

        logger.info('CodeImageView GET request')

        # render response
        response_OUT = self.process_request( request )

        return response_OUT

    #-- END method get() --#

    def post( self, request ):

        # return reference
        response_OUT = None

        logger.info('CodeImageView POST request')

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
            logger.error( "Multiple breakers for image {image}. Not good.".format( image = image_IN ) )

        #-- END check if single breaker. --#

        context_OUT[ CONTEXT_BREAKER_INSTANCE ] = my_breaker

        # set up form.
        field_qs = FormField.objects.filter( year = image_IN.year )
        field_qs = field_qs.filter( form_type = "breaker" )
        logger.info( f'{me}: FormField query length was {len(field_qs)}' )
        breaker_fields = [f.field_name for f in list(field_qs)]

        BreakerFormSet = modelformset_factory( Breaker, fields = breaker_fields, formset = BaseBreakerFormSet, extra = formset_extra_count )
        formset = BreakerFormSet( queryset = breaker_qs )

        context_OUT[ CONTEXT_BREAKER_FORMSET ] = formset

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
        context_OUT[ "slug" ] = image_IN.image_file.img_file_name

        # does image have related objects?
        image_has_related_objects = image_IN.has_related_objects()

        # does image have related objects?
        if ( image_has_related_objects == False ):

            # no - OK to still make the fields editable...?
            # populate forms from database for existing rows.
            image_form_values = dict()
            image_form_values[ PARAM_NAME_YEAR ] = image_IN.year
            image_form_values[ PARAM_NAME_IMAGE_TYPE ] = image_IN.image_type

            # create image form(s).
            image_form = ImageForm( image_form_values )

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
        this_longform = None

        # look up existing instance for this image
        longform_qs = image_IN.longform1990_set.all()

        # there shouldn't be more than one
        if longform_qs.count() == 1:
            this_longform = longform_qs.get()
        elif longform_qs.count() > 1:
            logger.error(f"Multiple 1990 long forms associated with image {image_IN}.")

        context_OUT[ CONTEXT_LONGFORM_INSTANCE ] = this_longform

        # define fields based on which year it is
        fields = get_form_fields(1990, 'long') 
        field_widgets = {f: choices.FORM_WIDGETS[f] for f in fields if f in choices.FORM_WIDGETS}

        # - render form, populated if there is already a longform
        #     instance for this image.
        this_form = modelform_factory(LongForm1990, fields=fields, widgets = field_widgets)
        helper = LongFormHelper(year=1990)


        context_OUT[ CONTEXT_LONGFORM_FORM ] = this_form
        context_OUT[ CONTEXT_LONGFORM_HELPER ] = helper

        logger.info(f'{me}: context_OUT is {context_OUT}')

        return context_OUT


    def prepare_other_image_context( self, image_IN, context_IN ):
        
        me = 'CodeImageView.prepare_other_image_context'

        # inits
        context_OUT = context_IN
        this_other_image = None

        # look up existing instance for this image
        other_image_qs = image_IN.otherimage_set.all()

        logger.info(f"{me}(): other_image_qs is {other_image_qs}")

        # there shouldn't be more than one
        if other_image_qs.count() == 1:
            this_other_image = other_image_qs.get()
        elif other_image_qs.count() > 1:
            logger.error(f"Multiple OtherImages associated with image {image_IN}.")

        logger.info(f"{me}(): this_other_image is {this_other_image}")

        context_OUT[ CONTEXT_OTHER_IMAGE_INSTANCE ] = this_other_image

        # - render form, populated if there is already an OtherImage
        #     instance for this image.
        this_form = OtherImageForm( instance =  this_other_image )

        context_OUT[ CONTEXT_OTHER_IMAGE_FORM ] = this_form

        logger.info(f'{me}: context_OUT is {context_OUT}')

        return context_OUT


    def prepare_record_context( self, image_IN, context_IN ):

        me = 'CodeImageView.prepare_record_context'

        # add on to context passed in
        context_OUT = context_IN

        # look up parent sheet instance (relying on Jon's error check in prepare_sheet_context)
        parent_sheet = image_IN.sheet_set.get()  

        # look up associated record(s)
        record_qs = parent_sheet.record_set.all()
        record_count = record_qs.count()

        # DEBUG
        logger.info(f'{me}: record_count is {record_count}')
        logger.info(f'{me}: context_IN is {context_IN}')


        # set up form.
        record_fields = get_form_fields( parent_sheet.year, 'short' ) #TODO: THIS SHOULD NOT BE HARD-CODED
        field_widgets = {f: choices.FORM_WIDGETS[f] for f in record_fields if f in choices.FORM_WIDGETS}

        RecordForm = modelform_factory(Record, fields = record_fields, widgets = field_widgets)
        helper = RecordFormHelper(year=parent_sheet.year)

        if CONTEXT_RECORD_INSTANCE in context_IN.keys():
            record_instance = context_IN[ CONTEXT_RECORD_INSTANCE ]
        else:
            record_instance = None
        logger.info(f"{me}(): record_instance is {record_instance}")

        if record_instance:
            form = RecordForm(instance = record_instance)
        else:
            form = RecordForm()

        context_OUT[ CONTEXT_RECORD_FORM ] = form
        context_OUT[ CONTEXT_RECORD_FORMSET_HELPER ] = helper
        context_OUT[ CONTEXT_RECORD_INSTANCE ] = record_instance
        context_OUT[ CONTEXT_RECORD_LIST ] = record_qs


        logger.info(f'context returned from prepare_record_context {context_OUT}')

        return context_OUT

    #-- END method prepare_record_context() --#


    def prepare_sheet_context( self, image_IN, context_IN ):

        # return reference
        context_OUT = None

        # declare variables
        me = 'CodeImage.prepare_sheet_context'
        sheet_qs = None
        sheet_count = None
        this_sheet = None
        this_form = None

        # add on to context passed in.
        context_OUT = context_IN

        # - look up sheet instance for this image (could be None).
        # is there an existing Sheet instance?
        sheet_qs = image_IN.sheet_set.all()
        sheet_count = sheet_qs.count()
        if ( sheet_count == 1 ):
            this_sheet = sheet_qs.get()
        elif ( sheet_count > 1 ):
            logger.error( "Multiple sheets for image {image}. Not good.".format( image = image_IN ) )
        #-- END check if single sheet. --#

        context_OUT[ CONTEXT_SHEET_INSTANCE ] = this_sheet

        # - render sheet form, populated if there is already a sheet
        #     instance for this image.
        this_form = SheetForm( instance = this_sheet )
        context_OUT[ CONTEXT_SHEET_FORM ] = this_form

        # - if sheet instance:
        #     - render record form, prepopulate if record ID is present.
        #     - pull in records, sorted by row ID, and then output list with
        #         edit link next to each.
        if this_sheet:
            context_OUT = self.prepare_record_context( image_IN, context_OUT )

        # logger.info(f'{me}: context_OUT is {context_OUT}')

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
                    logger.info(f'CodeImageView.process_action() action is {my_action}')
                    
                    if ( my_action == ACTION_COMPLETE_IMAGE ):
                        
                        # mark image as complete
                        action_error_list = self.action_complete_image( request_IN, context_IN ) 
                    
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

        # declare variables
        me = "CodeImage.process_request"
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
        seed_current_entry( request ) # this ensures there's a value in CurrentEntry
        get_next_image( request )

        # get request inputs (get or post)
        request_inputs = get_request_data( request )

        # get current user info
        logger.info(f'{me} user info:\n \t {request.user}')
        current_user = request.user.username
        context[ "user" ] = current_user

        logger.info(f'CodeImageView.process_request(): request_inputs are {request_inputs}')

        # get IDs of image to process.
        current_image_id = request_inputs.get( PARAM_NAME_IMAGE_ID, None )

        # do we have an image ID?
        if ( ( current_image_id is not None ) and ( current_image_id != "" ) ):

            # is there an action?
            my_action = request_inputs.get( PARAM_NAME_ACTION, None )
            logger.info(f"{me}() my_action is {my_action}")
            if ( ( my_action is not None ) and ( my_action in VALID_ACTIONS ) ):

                # process action
                got_action = True
                returned_error_list = self.process_action( request, context )
                if ( ( returned_error_list is not None ) and ( len( returned_error_list ) > 0 ) ):
                    error_list.extend( returned_error_list )
                #-- END check if process_action errors. --#

                # if the action is complete_image, update_breaker_type, update_other_image, we return to the index
                if my_action in [ACTION_COMPLETE_IMAGE, ACTION_UPDATE_OTHER_IMAGE, ACTION_UPDATE_BREAKER_TYPE]:
                    
                    return redirect(reverse("EntryApp:index"))
                
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
                context = self.prepare_sheet_context( current_image, context )
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

        response_OUT = render( request, return_template_name, context )

        return response_OUT

    #-- END method process_request() --#

#-- END class CodeImage --#

#------------------------------------------------------------------------------#
# PROBLEM VIEW
#------------------------------------------------------------------------------#

def parse_http_referral(url):
    '''
    Helper function for report_problem view
    Parses referring url from HTTP request to extract site of problem

    Takes: string from the HTTP request referring url
    Returns: string name of model affected
    '''
    if url:
        page_name = re.search('(?<=EntryApp/).+/', url).group(0)[:-1]
        logger.info(f"parse_http_referral: {page_name}")
        return page_name
    else:
        logger.info(f'parse_http_referral did not get a url, returning empty string.')
        return ""


@login_required
def report_problem(request):
    '''
    View to render problem form so user can record an issue
    '''

    current = CurrentEntry.objects.get(jbid=request.user)
    flagged_view = None

    if request.method == "GET":

        inputs_IN = get_request_data(request)

        # did we get image ID? 
        image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )

        if image_id:

            image_instance = Image.objects.get(pk=image_id)

            logger.info(f'report_problem GET request for {image_id}')
            logger.info(f"report_problem referred from {request.META['HTTP_REFERER']}")
            flagged_view = parse_http_referral(request.META['HTTP_REFERER'])
            return render(
                    request, \
                    'EntryApp/report-problem.html',
                    {
                        'image': image_instance,
                        'slug': image_instance.image_file.image_file_name,
                        'form': ProblemForm()
                    }
            )
        else:
            
            logger.info(f"report_problem GET request with no image id")
            logger.info(f"report_problem referred from {request.META['HTTP_REFERER']}")

            return render(
                request,
                'EntryApp/report-problem.html',
                {
                    'form': ProblemForm()
                }
            )

    elif request.method == "POST":

        form = request.POST
        problem_image = current.img
        logger.info(f'report_problem POST request for {current.img.img_path}')
        logger.info(f'report_problem problem_image pk is {problem_image.pk}')

        # do I need to figure out what kind of image it is?
        try:

            # flag the problem at the image level
            is_problem = True if 'problem' in form.keys() else False

            if problem_image.is_complete:
                defaults = {
                    'problem': is_problem,
                    'prob_description': form['description'],
                    'flagged_view': flagged_view
                }

            else:
                defaults = {
                    'is_complete': True,
                    'problem': is_problem,
                    'prob_description': form['description'],
                    'flagged_view': flagged_view
                }

            problem_image, updated = Image.objects.update_or_create(
                jbid = request.user,
                pk = problem_image.pk,
                defaults = defaults
            )

            return redirect(reverse('EntryApp:index'))

        except Exception as e:
            logger.warn(f"Exception in report_problem: ", e)
            return render(
                request, \
                'EntryApp/report-problem.html',
                {
                    'image': current.img,
                    'slug': current.img.image_file.image_file_name,
                    'form': ProblemForm()
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
# DUMMY VIEWS
#------------------------------------------------------------------------------#

def test_crispy_formset_view(request, year):
    '''
    View for testing django crispy formsets
    '''

    field_q = FormField.objects.filter(year=year).filter(form_type='short')
    fields = [f.field_name for f in list(field_q)]
    logger.info(f'crispy formset fields are {fields}')
    TestCrispyFormset = modelformset_factory(
        Record,
        fields=fields,
        extra=2,
        formset=BaseRecordFormSet,
        widgets = {
            'relp_1960': forms.RadioSelect,
            'relp_1970': forms.RadioSelect,
            'relp_1980': forms.RadioSelect,
            'relp_1990': forms.RadioSelect,
            'sex': forms.RadioSelect,
            'race_1960': forms.RadioSelect,
            'race_1970': forms.RadioSelect,
            'race_1980': forms.RadioSelect,
            'race_1990': forms.RadioSelect,
            'birth_quarter': forms.RadioSelect,
            'birth_decade': forms.RadioSelect,
            'birth_year': forms.RadioSelect,
            'marital_status': forms.RadioSelect,
            'age_hundreds': forms.RadioSelect,
            'age_tens': forms.RadioSelect,
            'age_ones': forms.RadioSelect,
            'birth_year_thousands': forms.RadioSelect,
            'birth_year_hundreds': forms.RadioSelect,
            'birth_year_tens': forms.RadioSelect,
            'birth_year_ones': forms.RadioSelect,
            'block_1': forms.RadioSelect,
            'block_2': forms.RadioSelect,
            'block_3': forms.RadioSelect,
            'serial_no_1':forms.RadioSelect,
            'serial_no_2':forms.RadioSelect,
            'serial_no_3':forms.RadioSelect,
            'serial_no_4':forms.RadioSelect,
            'serial_no_5':forms.RadioSelect,
            'serial_no_6':forms.RadioSelect,
            'serial_no_7':forms.RadioSelect,
            'serial_no_8':forms.RadioSelect,
            'serial_no_9':forms.RadioSelect,
            'serial_no_10':forms.RadioSelect,
            'serial_no_11':forms.RadioSelect,
            'total_persons_hundreds': forms.RadioSelect,
            'total_persons_tens': forms.RadioSelect,
            'total_persons_ones': forms.RadioSelect,
        }
    )
    formset = TestCrispyFormset()
    helper = CrispyFormSetHelper(year=year)
    context = {
        'formset': formset,
        'helper': helper
    }
    return render(request, 'EntryApp/test-crispy-formset.html', context)
