import logging
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views.generic import FormView, TemplateView

from EntryApp.models import Image, Sheet
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

    # watch out for all complete - this object would then be None    
    new_image =  Image.objects.filter(is_complete=False)[0]


    def post(self, form):
        """
        Take user input of year + image type into DB
        """
        logger.info(f'form.cleaned_data is {form.cleaned_data}')

        self.new_image.year = form.cleaned_data['year']
        self.new_image.image_type = form.cleaned_data['image_type'].lower()
        self.new_image.save()
        
        return f"EntryApp/enter-{self.new_image.image_type}-data.html"




class EnterSheetData(FormView):
    
    form_class = SheetForm

    sheet = Sheet.objects.filter(img_path=img_path)

    

    def post(self, request):
        
        form = self.form_class(request.POST)

        if form.is_valid():

            logger.info(f'SheetForm cleaned_data is {form.cleaned_data}')

            


class EnterBreakerData(FormView):
    
    def get(self, request):
        return render(request, 'EntryApp/enter-breaker-data.html')



def ThankYou(request):
    """
    Dummy class for dev
    """
    return render(request, 'EntryApp/thank-you.html')    