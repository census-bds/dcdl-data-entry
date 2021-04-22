"""
VIEWS FOR DCDL DATA ENTRY

TO DO:
-integrate openseadragon info into views
"""
import datetime
import logging
import re

from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import View, FormView, TemplateView, CreateView, ListView
from django.forms import formset_factory, modelformset_factory, RadioSelect
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import loader
from django.template import RequestContext
from django.template.context_processors import csrf

# EntryApp models
from EntryApp.models import Breaker
from EntryApp.models import CurrentEntry
from EntryApp.models import FormField
from EntryApp.models import Image
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Sheet

# EntryApp forms
from EntryApp.forms import BaseBreakerFormSet
from EntryApp.forms import BaseRecordFormSet
from EntryApp.forms import BreakerForm
from EntryApp.forms import ImageForm
from EntryApp.forms import ImageTypeForm
from EntryApp.forms import ImageYearForm
from EntryApp.forms import ProblemForm
from EntryApp.forms import RecordForm
from EntryApp.forms import SheetForm


#==============================================================================#
# CONSTANTS-ish
#==============================================================================#

# standard context names
CONTEXT_PARAM_NAMES = "param_names"
CONTEXT_ERROR_LIST = "error_list"

# input parameter names
PARAM_NAME_ACTION = "action"
PARAM_NAME_IMAGE_ID = "image_id"
PARAM_NAME_YEAR = "year"
PARAM_NAME_IMAGE_TYPE = "image_type"
PARAM_NAMES = {}
PARAM_NAMES[ "PARAM_NAME_IMAGE_ID" ] = PARAM_NAME_IMAGE_ID
PARAM_NAMES[ "PARAM_NAME_ACTION" ] = PARAM_NAME_ACTION
PARAM_NAMES[ "PARAM_NAME_YEAR" ] = PARAM_NAME_YEAR
PARAM_NAMES[ "PARAM_NAME_IMAGE_TYPE" ] = PARAM_NAME_IMAGE_TYPE

# actions
ACTION_UPDATE_IMAGE = "update_image"
ACTION_UPDATE_TYPE = "update_type"
ACTION_UPDATE_RECORD = "update_record"
VALID_ACTIONS = []
VALID_ACTIONS.append( ACTION_UPDATE_IMAGE )
VALID_ACTIONS.append( ACTION_UPDATE_TYPE )
VALID_ACTIONS.append( ACTION_UPDATE_RECORD )

#==============================================================================#
# variables
#==============================================================================#

logger = logging.getLogger('EntryApp.views')

#==============================================================================#
# functions
#==============================================================================#

def get_next_image(request):
    '''
    Helper function for BeginNewImageView
    Look up next image for user to enter and put it in CurrentEntry
    '''

    # refine this, probably
    try:
        new_image = Image.objects.filter(is_complete=False).filter(jbid=request.user)[0]
        logger.info(f'get_new_image got {new_image.img_path}')

        if new_image:
            current = CurrentEntry.objects.get(jbid=request.user)
            current.img = new_image
            current.save()

    except Exception as e:
        print(e)
        raise Http404("get_next_image might not have found images to enter.")

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


def initialize_context( request_IN, dict_IN = None ):

    '''
    Accepts request, optional context dictionary. If no dictionary passed in,
        makes a new one. Does standard initialization, returns initialized
        dictionary.
    '''

    # return reference
    dict_OUT = None

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

    return dict_OUT

#-- END function initialize_context() --#


def seed_current_entry(request):
    '''
    Helper function for BeginNewImageView: Put dummy data into current entry
     table. It should only be called for the first image for each user.
    '''
    if CurrentEntry.objects.filter(jbid=request.user):
        return

    else:
        # these will be overwritten, I think, so values don't matter
        logger.info(f'seed_current_entry inserting into CurrentEntry')
        an_image = Image.objects.all()[0]
        a_breaker = Breaker.objects.create(jbid=request.user, img=an_image)
        current = CurrentEntry.objects.create(jbid=request.user, \
                                            img=an_image, \
                                            breaker = a_breaker, \
                                            sheet = None)
        a_breaker.delete() # delete temp breaker from Breaker model

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
        completed_count = None
        next_image = None
        context = None

        # init
        recent_image_count = 5
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
        todo_image_qs = user_image_qs.filter( is_complete = False )
        todo_image_qs = todo_image_qs.order_by( 'image_file__img_reel_label', 'image_file__img_reel_index', 'image_file__img_position' )
        todo_image_count = todo_image_qs.count()
        next_image = todo_image_qs.first()
        context[ 'num_todo' ] = todo_image_count
        context[ 'next_image' ] = next_image

        # done
        recent_image_qs = user_image_qs.filter( is_complete = True )
        recent_image_qs = recent_image_qs.order_by( '-last_modified' )
        completed_count = recent_image_qs.count()
        context[ 'num_completed' ] = completed_count

        # limit to recent_image_count, and add QS to context.
        recent_image_qs = recent_image_qs[ : recent_image_count ]
        recent_image_list = list(  )
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

    def old_post( self, request ):
        try:
            form = request.POST
            logger.info(f'BeginNewImage post() form is {form}')
            current = CurrentEntry.objects.get(jbid=request.user)
            image, created = Image.objects.update_or_create(
                img_path = current.img.img_path,
                jbid = request.user,
                defaults = {'year': form['year'],
                'image_type': form['image_type'].lower(),
                'is_complete': True,
                'timestamp': datetime.datetime.now()
                }
            )
            logger.info(f'BeginNewImage post() current image is {image}')

            return redirect(reverse(f'EntryApp:enter_{image.image_type}_data'))

        except KeyError:
            logger.info("KeyError in post() for BeginNewImage")
            return render(request, 'EntryApp/begin-new-image.html')

    #-- END method old_post --#


    def action_update_image( self, inputs_IN ):

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
        image_id = None
        image_instance = None
        year_value = None
        image_type_value = None
        is_changed = None

        # init
        error_list_OUT = list()

        # got inputs?
        if ( ( inputs_IN is not None ) and ( len( inputs_IN ) > 0 ) ):

            # get image for ID (TODO: check for image ID)
            image_id = inputs_IN.get( PARAM_NAME_IMAGE_ID, None )
            image_instance = Image.objects.get( pk = image_id )

            # get image info from form inputs.

            # year
            year_value = inputs_IN.get( PARAM_NAME_YEAR, None )

            # got a value?
            if ( ( year_value is not None ) and ( year_value != "" ) ):

                # different?
                year_value = int( year_value )
                if ( year_value != image_instance.year ):

                    # changed value!

                    # TODO: check if there are any child rows. If so, reject change.

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

                    # TODO: check if there are any child rows. If so, reject change.

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

            # no inputs?
            error_message = "In {method}(): No inputs passed in. What is going on?".format( method = me )
            error_list_OUT.append( error_message )

        #-- END check if inputs. --#

        return error_list_OUT

    #-- END method action_update_image() --#


    def get( self, request ):

        # return reference
        response_OUT = None

        # render response
        response_OUT = self.process_request( request )

        return response_OUT

    #-- END method get() --#

    def post( self, request ):

        # return reference
        response_OUT = None

        # render response
        response_OUT = self.process_request( request )

        return response_OUT

    #-- END method post() --#


    def process_action( self, request_IN ):

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
        context = initialize_context( request )
        error_list = list()
        request = request_IN

        # got request?
        if ( request_IN is not None ):

            # get request inputs (get or post)
            request_inputs = get_request_data( request )

            # get IDs of image to process.
            current_image_id = request_inputs.get( PARAM_NAME_IMAGE_ID, None )

            # do we have an image ID?
            if ( ( current_image_id is not None ) and ( current_image_id != "" ) ):

                # is there an action?
                my_action = request_inputs.get( PARAM_NAME_ACTION, None )
                if ( ( my_action is not None ) and ( my_action in VALID_ACTIONS ) ):

                    # what action?
                    action_error_list = None
                    if ( my_action == ACTION_UPDATE_IMAGE ):

                        # update the image
                        action_error_list = self.action_update_image( request_inputs )

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
        request_inputs = None
        current_user = None
        current_username = None
        request_inputs = None
        current_image_id = None
        current_action = None
        image_qs = None
        current_image = None
        context = None
        error_message = None
        error_list = None
        my_action = None
        got_action = None
        returned_error_list = None

        # declare variables - image forms
        image_form_values = None
        image_year_form = None
        image_type_form = None

        # init
        context = initialize_context( request )
        error_list = list()

        # get request inputs (get or post)
        request_inputs = get_request_data( request )

        # get current user info
        logger.info(f'user info:\n \t {request.user}')
        current_user = request.user
        current_username = current_user.username
        context[ "user" ] = current_user

        # get IDs of image to process.
        current_image_id = request_inputs.get( PARAM_NAME_IMAGE_ID, None )

        # do we have an image ID?
        if ( ( current_image_id is not None ) and ( current_image_id != "" ) ):

            # is there an action?
            my_action = request_inputs.get( PARAM_NAME_ACTION, None )
            if ( ( my_action is not None ) and ( my_action in VALID_ACTIONS ) ):

                # process action
                got_action = True
                returned_error_list = self.process_action( request )
                if ( ( returned_error_list is not None ) and ( len( returned_error_list ) > 0 ) ):
                    error_list.extend( returned_error_list )
                #-- END check if process_action errors. --#

            #-- END check to see if action. --#

            # retrieve image
            image_qs = Image.objects.filter( pk = current_image_id )
            current_image = image_qs.get()

            # TODO: break out creating image forms into form_image() method?
            # - do not render forms at all if image has a child for its type.
            # - this means going back to single ImageForm, if you add it to
            #     context, output form, if not present, just output image
            #     information and note on problem reporting.
            # - still want to add this same check to the action method, so you
            #     don't update if child already exists.
            # - create method on Image to check for child type, return True if
            #     one found, false if not.

            # populate forms from database for existing rows.
            image_form_values = dict()
            image_form_values[ PARAM_NAME_YEAR ] = current_image.year
            image_form_values[ PARAM_NAME_IMAGE_TYPE ] = current_image.image_type

            # create image form(s).
            image_year_form = ImageYearForm( image_form_values )
            image_type_form = ImageTypeForm( image_form_values )
            context[ "img" ] = current_image
            context[ "image_year_form" ] = image_year_form
            context[ "image_type_form" ] = image_type_form
            context[ "slug" ] = current_image.image_file.img_path

            # TODO: what type?

            # TODO: if breaker:
            # - look up breaker instance for this image (could be None).
            # - render breaker form, populated if there is already a breaker
            #     instance for this image.
            # - pull in images, link to edit each, OR link to edit next image.

            # TODO: if sheet:
            # - look up sheet instance for this image (could be None).
            # - render sheet form, populated if there is already a breaker
            #     instance for this image.
            # - if sheet instance:
            #     - render record form.
            #     - pull in records, sorted by row ID, and then output list with
            #         edit link next to each.

        else:

            # no image ID. Error. can not proceed.
            error_list.append( "No image ID found in request, can't code image." )

        #-- END check to see if image ID passed in. --#

        # errors?
        if ( ( error_list is not None ) and ( len( error_list ) > 0 ) ):

            # store it.
            context[ CONTEXT_ERROR_LIST ] = error_list

        #-- END check for error list --#

        response_OUT = render( request, self.template_name, context )

        return response_OUT

    #-- END method process_request() --#

#-- END class CodeImage --#


#------------------------------------------------------------------------------#
# IMAGE
#------------------------------------------------------------------------------#

class BeginNewImageView(LoginRequiredMixin, FormView):

    form_class = ImageForm
    template_name = 'EntryApp/begin-new-image.html'

    def get(self, request):

        seed_current_entry(request) # this ensures there's a value in CurrentEntry
        get_next_image(request) # this loads the next image into CurrentEntry

        img = CurrentEntry.objects.get(jbid=request.user).img
        context = {
            'image': img,
            'form': self.form_class(),
            'slug': img.img_path
        }
        return render(request, self.template_name, context)

    def post(self, request):
        try:
            form = request.POST
            logger.info(f'BeginNewImage post() form is {form}')
            current = CurrentEntry.objects.get(jbid=request.user)
            image, created = Image.objects.update_or_create(
                img_path = current.img.img_path,
                jbid = request.user,
                defaults = {'year': form['year'],
                'image_type': form['image_type'].lower(),
                'is_complete': True,
                'timestamp': datetime.datetime.now()
                }
            )
            logger.info(f'BeginNewImage post() current image is {image}')

            return redirect(reverse(f'EntryApp:enter_{image.image_type}_data'))

        except KeyError:
            logger.info("KeyError in post() for BeginNewImage")
            return render(request, 'EntryApp/begin-new-image.html')



#------------------------------------------------------------------------------#
# BREAKER
#------------------------------------------------------------------------------#

class EnterBreakerData(LoginRequiredMixin, FormView):

    template_name = 'EntryApp/enter-breaker-data.html'

    def get(self, request):
        logger.info(f'breaker request is {request}')

        current = CurrentEntry.objects.get(jbid=request.user)

        field_query = FormField.objects.filter(year=current.img.year).filter(form_type="breaker")
        logger.info(f'FormField query length was {len(field_query)}')
        breaker_fields = [f.field_name for f in list(field_query)]

        BreakerFormSet = modelformset_factory(Breaker, fields=breaker_fields,formset=BaseBreakerFormSet)
        formset = BreakerFormSet(queryset=Breaker.objects.none)

        context = {
            'breaker_img_path': current.img.img_path,
            'formset': formset,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = request.POST
        logger.info(f'Breaker form is{form}')

        current = CurrentEntry.objects.get(jbid=request.user)

        # define fields based on which year it is
        field_query = FormField.objects.filter(year=current.img.year).filter(form_type="breaker")
        logger.info(f'FormField query length was {len(field_query)}')
        breaker_fields = [f.field_name for f in list(field_query)]

        BreakerFormSet = modelformset_factory(Breaker, fields=breaker_fields, formset=BaseBreakerFormSet)
        formset = BreakerFormSet(request.POST, request.FILES)

        logger.info(f'Breaker formset clean data should have length 1: {formset.cleaned_data}')

        try:
            b = formset.cleaned_data[0]
            b['img'] = current.img
            b['year'] = current.img.year
            b['jbid'] = request.user
            b['timestamp'] = datetime.datetime.now()
            breaker, created = Breaker.objects.update_or_create(**b)
            logger.info(f'submit_breaker update_or_create() returned {created}')

            # next update CurrentEntry
            current = CurrentEntry.objects.get(jbid=request.user)
            current.breaker = breaker
            current.save()

            return redirect(reverse('EntryApp:index'))

        except KeyError:
            logger.warn("KeyError in submit_breaker post()")
            return render(request, reverse(self.template_name))


#------------------------------------------------------------------------------#
# SHEET
#------------------------------------------------------------------------------#

class EnterSheetData(LoginRequiredMixin, FormView):

    form_class = SheetForm
    template_name = 'EntryApp/enter-sheet-data.html'

    def get(self, request):
        '''
        Handle GET request and return page with empty form
        '''

        logger.info(f'EnterSheet GET request')
        current = CurrentEntry.objects.get(jbid=request.user)
        context = {
            'breaker': current.breaker,
            'form': self.form_class(),
            'slug': current.img.img_path,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        '''
        Handle POST request with populated form; save form data to DB
        '''

        form = request.POST
        logger.info(f'EnterSheet POST request form: {form}')

        try:
            # first save the data in Sheet
            current_img = CurrentEntry.objects.get(jbid=request.user).img

            # 1990 never has breakers, so assign the default dummy
            if current_img.year == 1990:
                # this breaker gets created for each user during data loading
                associated_breaker = Breaker.objects.filter(year=1990).get(jbid=request.user)
            else:
                associated_breaker = CurrentEntry.objects.get(jbid=request.user).breaker

            logger.info(f"associated breaker: {type(associated_breaker)}")
            sheet, created = Sheet.objects.update_or_create(
                img = current_img,
                jbid = request.user,
                year = current_img.year,
            defaults = {
                    'form_type': form['form_type'],
                    'breaker': associated_breaker,
                    'num_records': form['num_records'],
                    'timestamp': datetime.datetime.now()
                    }
            )
            logger.info(f'EnterSheetDataView update_or_create() returned {created}')

            # next update CurrentEntry
            current = CurrentEntry.objects.get(jbid=request.user)
            current.sheet = sheet
            current.save()

            return redirect(reverse('EntryApp:enter_records'))

        except KeyError:
            logger.warn("KeyError in submit_sheet post()")
            return render(request, reverse(self.template_name))


#------------------------------------------------------------------------------#
# RECORD
#------------------------------------------------------------------------------#

@login_required
def enter_records(request):
    '''
    View where the user can enter 1 or more person records
    '''

    # get the current metadata
    current = CurrentEntry.objects.get(jbid=request.user)
    num_records = current.sheet.num_records

    # this query would fail if sheet is None but that shouldn't happen
    logger.info(f'FormField: year of current entry is {current.img.year}')
    field_query = FormField.objects.filter(year=current.img.year).filter(form_type=current.sheet.form_type)
    logger.info(f'FormField query length was {len(field_query)}')
    record_fields = [f.field_name for f in list(field_query)]
    logger.info(f'form records fields are {record_fields}')


    RecordFormSet = modelformset_factory(
        Record,
        form=RecordForm,
        fields=record_fields,
        extra=num_records,
        formset=BaseRecordFormSet,
    )
    helper = CrispyFormSetHelper(
        year=current.img.year,
        form=current.sheet.form_type
    )

    if request.method == 'POST':

        logger.info(f'enter_record view POST request')
        formset = RecordFormSet(request.POST, request.FILES)
        logger.info(f'{formset.is_valid()}')

        if formset.is_valid():
            for r in formset.cleaned_data:
                r['sheet'] = current.sheet
                r['timestamp'] = datetime.datetime.now()
                r['jbid'] = request.user
                logger.info(f'record value is {r}')
                record, created = Record.objects.get_or_create(**r)

                if created:
                    logger.info(f'{record} created.')
                else:
                    logger.info(f'{record} updated.')

            return redirect(reverse('EntryApp:index'))

    else:
        formset = RecordFormSet(queryset=Record.objects.none)

    context = {
        'formset': formset,
        'helper': helper,
        'slug': current.img.img_path
    }
    return render(request, 'EntryApp/enter-records.html', context)

#------------------------------------------------------------------------------#
# VIEW RECENT IMAGES
#------------------------------------------------------------------------------#

class ListRecentView(LoginRequiredMixin, ListView):
    '''
    View to list 5 most recent entries in case editing is needed
    '''
    model = Image
    template_name = 'EntryApp/list-recent.html'

    def get_queryset(self):
        jbid = self.request.user
        return Image.objects.filter(jbid=jbid) \
                            .filter(is_complete=True) \
                            .order_by('-timestamp')[1:5] # FIX THIS LATER


#------------------------------------------------------------------------------#
# EDIT VIEW
#------------------------------------------------------------------------------#

@login_required
def edit_entry(request):
    '''
    Edit details that have already been entered

    IMPLEMENTATION TBD
    '''
    pass



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
        logger.info(f'report_problem GET request for {current.img.img_path}')
        logger.info(f"report_problem referred from {request.META['HTTP_REFERER']}")
        flagged_view = parse_http_referral(request.META['HTTP_REFERER'])
        return render(
                request, \
                'EntryApp/report-problem.html',
                {
                    'image': current.img,
                    'slug': current.img.img_path,
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
                    'slug': current.img.img_path,
                    'form': ProblemForm()
                }
        )

#------------------------------------------------------------------------------#
# DUMMY VIEWS
#------------------------------------------------------------------------------#

from EntryApp.forms import CrispyFormSetHelper
import django.forms as forms

def test_crispy_formset_view(request, year):
    '''
    View for testing django crispy formsets
    '''

    field_q = FormField.objects.filter(year=year).filter(form_type='long')
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
    helper = CrispyFormSetHelper(year=year, form='long')
    context = {
        'formset': formset,
        'helper': helper
    }
    return render(request, 'EntryApp/test-crispy-formset.html', context)
