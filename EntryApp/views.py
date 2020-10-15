"""
VIEWS FOR DCDL DATA ENTRY

TO DO:
-a lot
"""
import logging
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse 
from django.views.generic import View, FormView, TemplateView, CreateView

from EntryApp.models import Breaker, Image, Sheet, CurrentEntry
from EntryApp.forms import ImageForm, SheetForm, BreakerForm

logger = logging.getLogger('EntryApp.views')


class IndexView(TemplateView):
    """
    Define view for app landing page
    """

    def get(self, request):
        latest_image_list = Image.objects.all()
        context = {
            'latest_image_list': latest_image_list
            }
        return render(request, 'EntryApp/index.html', context)


def seed_current_entry():
    '''
    Put dummy data into current entry table
    I think I only need this once for each user...
    ''' 
    if CurrentEntry.objects.all():
        return 
    
    else:

        # these will be overwritten, I think, so values don't matter
        an_image = Image.objects.all()[0]
        a_breaker = Breaker.objects.all()[0]

        current = CurrentEntry(jbid="jbid123", \
                                img=an_image, \
                                breaker = a_breaker, \
                                sheet = None)
        current.save()


def get_next_image():
    '''
    Look up next image for user to enter
    '''

    # refine this 
    new_image = Image.objects.filter(is_complete=False)[0]

    if new_image:
        current = CurrentEntry.objects.get(jbid='jbid123')
        current.save()
    else:
        raise Http404("Images are all complete.")


class BeginNewImageView(FormView):
    
    form_class = ImageForm
    template_name = 'EntryApp/begin-new-image'

    def get(self, request):

        # logger.info(f'dir of image request is {dir(request)}')
        seed_current_entry() # this ensures there's a value in CurrentEntry
        get_next_image() # this loads the next image into CurrentEntry

        context = {
            'image': CurrentEntry.objects.get(jbid='jbid123').img,
            'form': self.form_class()
        }
        return render(request, 'EntryApp/begin-new-image.html', context)

    
def submit_image(request):
    '''
    View to submit image data from the ImageForm
    '''
    form = request.POST
    logger.info(form)
    try:
        current_id = CurrentEntry.objects.get(jbid='jbid123').img.id
        current = Image.objects.get(id=current_id)
        current.year = form['year']
        current.image_type = form['image_type'].lower()
        # current.is_complete = True
        logger.info(f'submit_image POST current value is {current}')
        current.save()

        return redirect(reverse('EntryApp:enter_breaker_data'))

    except KeyError:
        logger.info("KeyError in submit_image")
        return render(request, 'EntryApp/begin-new-image.html')    


class EnterBreakerData(FormView):

    form_class = BreakerForm
    template_name = 'EntryApp/enter-breaker-data.html'
    
    def get(self, request):
        logger.info(f'breaker request is {request}')
        context = {
            'breaker_img_path': CurrentEntry.objects.get(jbid='jbid123').img.img_path,
            'form': self.form_class()
        }
        return render(request, self.template_name, context)

def submit_breaker(request):
    '''
    View to submit breaker data, definitely redundant
    '''
    form = request.POST
    logger.info(f'Breaker form is{form}')
    
    try:
        # first save the breaker data in Breaker
        current_img = CurrentEntry.objects.get(jbid='jbid123').img
        breaker, created = Breaker.objects.get_or_create(
            img = current_img,
            year = form['year'],
            state = form['state'],
            county = form['county']
        )
        logger.info(f'get_or_create() returned {created}')

        # next update CurrentEntry
        current = CurrentEntry.objects.get(jbid='jbid123')
        current.breaker = breaker
        current.save()

        return redirect(reverse('EntryApp:index'))

    except KeyError:
        logger.warn("KeyError in submit_breaker post()")
        return render(request, reverse('EntryApp:enter_breaker_data'))
    


class EnterSheetData(FormView):
    
    form_class = SheetForm
    sheet = None

    def get(self, request):

        sheet = None


    def post(self, request):
        
        form = self.form_class(request.POST)

        if form.is_valid():

            logger.info(f'SheetForm cleaned_data is {form.cleaned_data}')


def ThankYou(request):
    """
    Dummy class for dev
    """
    return render(request, 'EntryApp/thank-you.html')    