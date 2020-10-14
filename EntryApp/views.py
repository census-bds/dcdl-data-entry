import logging
from django.http import Http404
from django.shortcuts import get_object_or_404, render, reverse
from django.http import HttpResponse
from django.views.generic import View, FormView, TemplateView, CreateView

from EntryApp.models import Breaker, Image, Sheet
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
    
    def post(self, request):
        get_next_image(request)
        

def get_next_image(request):
    '''
    Look up next image for user to enter
    This should probably be in a class, but I don't know where...
    '''

    new_image = Image.objects.filter(is_complete=False)[0]

    if new_image:
        url = f'EntryApp/enter-image.html'
        context = {
            'image': new_image
        }
        return render(request, url, context)
    else:
        raise Http404("Images are all complete.")


class EnterImage(FormView):
    
    form_class = ImageForm
    template_name = "EntryApp/image.html"
    


def enter_image(request, pk):
    """
    Take user input of year + image type into DB
    """
    image = get_object_or_404(Image, pk=pk)
    form = request.POST
    try:
        image.year = form['year']
        image.image_type = form['image_type'].lower()
    except KeyError:
        return render(request, f'EntryApp/{image}/{pk}.html')
    else:
        # self.new_image.is_complete = True
        image.save()
    
        return render(request, f'EntryApp/{image.image_type}/{image.pk}.html')


class EnterSheetData(FormView):
    
    form_class = SheetForm
    sheet = None

    def get(self, request):

        sheet = None


    def post(self, request):
        
        form = self.form_class(request.POST)

        if form.is_valid():

            logger.info(f'SheetForm cleaned_data is {form.cleaned_data}')

            


class EnterBreakerData(FormView):

    form_class = BreakerForm
    template_name = 'EntryApp/enter-breaker-data.html'
    initial = {
        'image_id': None,
        'img_path': None,
        'breaker_id': None
        }
    
    def get(self, request):
        # self.initial['img_path'] = img_path
        context = {
            'form': BreakerForm()
        }
        return render(request, f'EntryApp/enter-breaker-data.html', context)


class CreateBreaker(CreateView):

    model = Breaker 
    fields = ['year', 'state', 'county', 'enum_dist']
    template_name = 'EntryApp/enter-breaker-data.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        


def ThankYou(request):
    """
    Dummy class for dev
    """
    return render(request, 'EntryApp/thank-you.html')    