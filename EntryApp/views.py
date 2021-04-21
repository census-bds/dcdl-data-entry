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
from django.contrib.auth.models import Permission, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, loader
from django.template.context_processors import csrf

from EntryApp.models import Image, Breaker, OtherImage, Sheet, Record, CurrentEntry, FormField
from EntryApp.forms import ImageForm, SheetForm, BreakerForm, RecordForm, BaseRecordFormSet, BaseBreakerFormSet, ProblemForm

#==============================================================================#
# CONSTANTS-ish
#==============================================================================#

# standard context names
CONTEXT_PARAM_NAMES = "param_names"

# input parameter names
PARAM_NAME_ACTION = "action"
PARAM_NAME_IMAGE_ID = "image_id"
PARAM_NAMES = {}
PARAM_NAMES[ "PARAM_NAME_IMAGE_ID" ] = PARAM_NAME_IMAGE_ID
PARAM_NAMES[ "PARAM_NAME_ACTION" ] = PARAM_NAME_ACTION

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

    - if sheet, then, edit records

        - if type is not sheet, do not output.
        - if record ID, load into edit form, if not, empty form.
        - output list of records, sorted by index. Beside each, output edit form.
    '''

    form_class = ImageForm
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

        # init
        context = initialize_context( request )

        # get request inputs (get or post)
        request_inputs = get_request_data( request )

        # get current user info
        logger.info(f'user info:\n \t {request.user}')
        current_user = request.user
        current_username = current_user.username
        context[ "user" ] = current_user

        # get ID of image to process.
        current_image_id = request_inputs.get( PARAM_NAME_IMAGE_ID, None )

        # do we have an image ID?
        if ( ( current_image_id is not None ) and ( current_image_id != "" ) ):

            # retrieve image
            image_qs = Image.objects.filter( pk = current_image_id )
            current_image = image_qs.get()

            context[ "img" ] = current_image
            context[ "form" ] = self.form_class()
            context[ "slug" ] = current_image.image_file.img_path

            response_OUT = render( request, self.template_name, context )

        #-- END check to see if image ID passed in. --#

        return response_OUT

    #-- END method process_request() --#

#-- END class CodeImage --#


#=====================================================#
# IMAGE
#=====================================================#

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


#=====================================================#
# BREAKER
#=====================================================#

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


#=====================================================#
# SHEET
#=====================================================#

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


#=====================================================#
# RECORD
#=====================================================#

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

#================================#
# VIEW RECENT IMAGES
#================================#

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


#================================#
# EDIT VIEW
#================================#

@login_required
def edit_entry(request):
    '''
    Edit details that have already been entered

    IMPLEMENTATION TBD
    '''
    pass



#================================#
# PROBLEM VIEW
#================================#

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

#================================#
# DUMMY VIEWS
#================================#

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
