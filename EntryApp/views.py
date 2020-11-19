"""
VIEWS FOR DCDL DATA ENTRY

TO DO:
-a lot
"""
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

from EntryApp.models import Breaker, Image, Sheet, CurrentEntry, Record
from EntryApp.forms import ImageForm, SheetForm, BreakerForm, BaseRecordFormSet

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
    template_name = 'EntryApp/begin-new-image'

    def get(self, request):

        seed_current_entry(request) # this ensures there's a value in CurrentEntry
        get_next_image(request) # this loads the next image into CurrentEntry

        context = {
            'image': CurrentEntry.objects.get(jbid=request.user).img,
            'form': self.form_class()
        }
        return render(request, 'EntryApp/begin-new-image.html', context)


@login_required
def seed_current_entry(request):
    '''
    Put dummy data into current entry table
    I think I only need this once for each user...
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


@login_required
def get_next_image(request):
    '''
    Look up next image for user to enter
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
    '''
    form = request.POST
    logger.info(form)
    try:
        current_id = CurrentEntry.objects.get(jbid=request.user).img.id
        image = Image.objects.get(id=current_id)
        image.year = form['year']
        image.image_type = form['image_type'].lower()
        image.is_complete = True # FOR DEV
        logger.info(f'submit_image POST current value is {image}')
        image.save() 

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
            'breaker_img_path': CurrentEntry.objects.get(jbid=request.user).img.img_path,
            'form': self.form_class()
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
        breaker, created = Breaker.objects.get_or_create(
            img = current_img,
            jbid = request.user,
            year = current_img.year,
            state = form['state'],
            county = form['county']
        )
        logger.info(f'submit_breaker get_or_create() returned {created}')

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
        context = {
            'breaker': CurrentEntry.objects.get(jbid=request.user).breaker,
            'form': self.form_class()
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
        
        sheet, created = Sheet.objects.get_or_create(
            img = current_img,
            year = current_img.year,
            jbid = request.user,
            form_type = form['form_type'],
            breaker = CurrentEntry.objects.get(jbid=request.user).breaker,
            num_records = form['num_records'],
            problem = is_problem
        )
        logger.info(f'submit_sheet get_or_create() returned {created}')

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

    # to do: implement this as a lookup based on curent year and form
    record_fields = [
        'row_num',
        'first_name',
        'middle_init',
        'last_name',
        'age',
        'sex'
    ]

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
        
    else:
        formset = RecordFormSet(queryset=Record.objects.none)
    
    return render(request, 'EntryApp/enter-records.html', {'formset': formset})


def export_records(request):
    '''
    '''

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachement; filename="records.csv"'

    writer = csv.writer(response)

    # change this so you can pick the table
    records = list(Record.objects.all())
    for r in records:
        writer.writerow([r.row_num, r.first_name, r.last_name])
    
    return response