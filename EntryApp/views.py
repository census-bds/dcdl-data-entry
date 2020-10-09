import logging
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
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
        


class BeginNewImageView(FormView):
    
    form_class = ImageForm
    template_name = "EntryApp/begin-new-image.html"
    # new_image = get_new_image()  # need to change implementation here I think

    # watch out for all complete - this object would then be None
    new_image = Image.objects.filter(is_complete=False)[0]
    # def get_new_image(self):
    #     return Image.objects.filter(is_complete=False)[0]

    def get(self, request):
        context = {
            'new_image': self.new_image,
            'form': self.form_class()
        }
        return render(request, 'EntryApp/begin-new-image.html', context)


    def post(self, request):
        """
        Take user input of year + image type into DB
        """
        form = self.form_class(request.POST)

        if form.is_valid():
            logger.info(f"form data is {form.cleaned_data}")
            self.new_image.year = form.cleaned_data['year']
            self.new_image.image_type = form.cleaned_data['image_type'].lower()
            # self.new_image.is_complete = True
            self.new_image.save()

            # url = f"EntryApp/enter-{self.new_image.image_type}-data/{self.new_image.img_path}.html"
            url = f"EntryApp/enter-{self.new_image.image_type}-data.html"
            # url = 'EntryApp/thank-you.html'
            return render(request, url)
        
        return render(request, "EntryApp/begin-new-image.html")


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