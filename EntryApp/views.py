"""
VIEWS FOR DCDL DATA ENTRY

TO DO:
-integrate openseadragon info into views
"""
import csv
import datetime
import logging
import re

from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse 
from django.views.generic import View, FormView, TemplateView, CreateView
from django.forms import formset_factory, modelformset_factory, RadioSelect
from django.contrib.auth.models import Permission, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, loader

from djqscsv import render_to_csv_response

from EntryApp.models import Image, Breaker, OtherImage, Sheet, Record, CurrentEntry, FormField
from EntryApp.forms import ImageForm, SheetForm, BreakerForm, RecordForm, BaseRecordFormSet, BaseBreakerFormSet, ExportForm, ProblemForm

logger = logging.getLogger('EntryApp.views')

#=====================================================#
# INDEX AND HELPER
#=====================================================#

class IndexView(LoginRequiredMixin, TemplateView):
    """
    Define view for app landing page
    """

    def get(self, request):

        logger.info(f'user info:\n \t {request.user}')
        latest_image_list = Image.objects.filter(jbid=request.user)
        user_complete_list = Image.objects.filter(jbid=request.user).filter(is_complete=True)
        context = {
            'user': request.user,
            'num_completed': len(user_complete_list), 
            'num_images': len(latest_image_list),
            }
        return render(request, 'EntryApp/index.html', context)


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
    Helper function for BeginNewImageView
    Put dummy data into current entry table
    I think I only need this once for each user... or fixtures make this irrelevant
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
        a_breaker.delete()


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
        widgets={
            'relp': RadioSelect,
            'sex': RadioSelect
        }
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
# EXPORT RECORDS VIEW
#================================#

class SelectExportFormView(LoginRequiredMixin, FormView):
    
    form_class = ExportForm
    template_name = 'EntryApp/select-record-export.html'

    def get(self, request):

        logger.info(f'ExportForm get request')
        context = {
            'form': self.form_class()
        }
        return render(request, self.template_name, context)

@login_required
def export_records(request):
    '''
    View that looks up selected model and gathers records for csv export
    '''

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename="records.csv"'
    writer = csv.writer(response)

    form = request.POST
    logger.info("export_records POST request")
    
    chosen_model = ExportForm.tables[int(form['table_choice'])]['model']
    
    records = chosen_model.objects.filter(jbid=request.user).values()
    return render_to_csv_response(records)

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

class TestImageView(LoginRequiredMixin, TemplateView):
    '''
    View for testing image types separately from rest of app
    '''

    def get(self, request):
        context = {'slug': 'tester_tiff_autumn.tif'}
        return render(request, 'test_dummy_image.html', context)

from EntryApp.forms import CrispyFormSetHelper 
import django.forms as forms

def test_crispy_formset_view(request):
    '''
    View for testing django crispy formsets
    '''

    field_q = FormField.objects.filter(year=1990).filter(form_type='short')
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
            'marital_status': forms.RadioSelect
        }
    )
    formset = TestCrispyFormset() 
    helper = CrispyFormSetHelper(year=1990, form='short')
    context = {
        'formset': formset,
        'helper': helper
    }
    return render(request, 'EntryApp/test-crispy-formset.html', context)