"""
VIEWS FOR DCDL DATA ENTRY

TO DO:
-convert to fully class-based views
-integrate openseadragon info into views
"""
import csv
import datetime
import logging

from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse 
from django.views.generic import View, FormView, TemplateView, CreateView
from django.forms import modelformset_factory
from django.contrib.auth.models import Permission, User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template import RequestContext, loader

from djqscsv import render_to_csv_response

from EntryApp.models import Breaker, Image, Sheet, CurrentEntry, Record, FormField
from EntryApp.forms import ImageForm, SheetForm, BreakerForm, BaseRecordFormSet, ExportForm

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
        context = {
            'user': request.user,
            'latest_image_list': latest_image_list
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
            'slug': img.img_path + '.jpg' 
        }
        return render(request, self.template_name, context)


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
        an_image = Image.objects.all()[0]
        a_breaker = Breaker.objects.all()[0]

        current = CurrentEntry(jbid=request.user, \
                                img=an_image, \
                                breaker = a_breaker, \
                                sheet = None)
        current.save()


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

            # # if there's nothing in current entry, insert image and empty breaker
            # if not current:
            #     current = CurrentEntry(
            #         img = new_image, \
            #         jbid = request.user, \
            #         breaker = Breaker(img = None), \
            #         sheet = None
            #     )
            #     current.save()

            # # otherwise we just update the image we're on
            # else:
            current.img = new_image
            current.save()

    except Exception as e:
        print(e)
        raise Http404("get_next_image might not have found images to enter.")


@login_required    
def submit_image(request):
    '''
    View to submit image data from the ImageForm
    This view has no template: it just submits and redirects
    '''
    form = request.POST
    logger.info(f'submit_image view got form {form}')

    try:
        current = CurrentEntry.objects.get(jbid=request.user)
        image, created = Image.objects.update_or_create(
            img_path = current.img.img_path, 
            jbid = request.user,
            defaults = {'year': form['year'],
            'image_type': form['image_type'].lower(),
            'is_complete': False # FOR DEV!!
            }
        )
        logger.info(f'submit_image POST current value is {image}')

        return redirect(reverse(f'EntryApp:enter_{image.image_type}_data'))

    except KeyError:
        logger.info("KeyError in submit_image")
        return render(request, 'EntryApp/begin-new-image.html')    

#=====================================================#
# BREAKER
#=====================================================#

class EnterBreakerData(LoginRequiredMixin, FormView):

    form_class = BreakerForm
    template_name = 'EntryApp/enter-breaker-data.html'
    
    def get(self, request):
        logger.info(f'breaker request is {request}')
        context = {
            'breaker_img_path': CurrentEntry.objects.get(jbid=request.user).img.img_path + '.jpg',
            'form': self.form_class(),
        }
        return render(request, self.template_name, context)


@login_required
def submit_breaker(request):
    '''
    View to submit breaker data
    '''
    form = request.POST
    logger.info(f'Breaker form is{form}')
    
    try:
        # first save the breaker data in Breaker
        current_img = CurrentEntry.objects.get(jbid=request.user).img
        breaker, created = Breaker.objects.update_or_create(
            img = current_img,
            jbid = request.user,
            defaults = {'year': current_img.year,
                        'state': form['state'],
                        'county': form['county']}
        )
        logger.info(f'submit_breaker update_or_create() returned {created}')

        # next update CurrentEntry
        current = CurrentEntry.objects.get(jbid=request.user)
        current.breaker = breaker
        current.save()

        return redirect(reverse('EntryApp:index'))

    except KeyError:
        logger.warn("KeyError in submit_breaker post()")
        return render(request, reverse('EntryApp:enter_breaker_data'))
    
#=====================================================#
# SHEET
#=====================================================#

class EnterSheetData(LoginRequiredMixin, FormView):
    
    form_class = SheetForm
    template_name = 'EntryApp/enter-sheet-data.html'

    def get(self, request):

        logger.info(f'EnterSheet get request')
        current = CurrentEntry.objects.get(jbid=request.user)
        context = {
            'breaker': current.breaker,
            'form': self.form_class(),
            'slug': current.img.img_path + '.jpg' 
        }
        return render(request, self.template_name, context)


@login_required
def submit_sheet(request):
    '''
    Function view to submit the data from the SheetForm
    '''

    form = request.POST 
    logger.info(f'submit_sheet form: {form}')

    try:
        # first save the data in Sheet 
        current_img = CurrentEntry.objects.get(jbid=request.user).img

        is_problem = form['problem'] if 'problem' in form.keys() else False
        if 'problem' in form.keys():
            logger.info(f"problem value is {form['problem']}")
        
        sheet, created = Sheet.objects.update_or_create(
            img = current_img,
            jbid = request.user,
            year = current_img.year,
           defaults = {
                'form_type': form['form_type'],
                'breaker': CurrentEntry.objects.get(jbid=request.user).breaker,
                'num_records': form['num_records'],
                'problem': is_problem
                }
        )
        logger.info(f'submit_sheet update_or_create() returned {created}')

        # next update CurrentEntry
        current = CurrentEntry.objects.get(jbid=request.user)
        current.sheet = sheet
        current.save()

        return redirect(reverse('EntryApp:enter_records'))

    except KeyError:
        logger.warn("KeyError in submit_sheet post()")
        return render(request, reverse('EntryApp:enter_sheet_data'))

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

    RecordFormSet = modelformset_factory(Record, fields=record_fields, extra=num_records, formset=BaseRecordFormSet)
    

    if request.method == 'POST':
        formset = RecordFormSet(request.POST, request.FILES)
        
        if formset.is_valid():
            for r in formset.cleaned_data:
                r['sheet'] = current.sheet
                r['entry_time'] = datetime.datetime.now()
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
        'slug': current.img.img_path + '.jpg'
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
    
    records = chosen_model.objects.all().values()
    return render_to_csv_response(records)