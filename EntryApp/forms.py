from django import forms 
from django.forms import formset_factory

from EntryApp.models import Breaker, Image, Record, Sheet, FormField

STATE_LIST = [
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', \
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', \
                'MI', 'MN', 'MS', 'MO',	'MT', 'NE',	'NV', 'NH',	'NJ', 'NM',	'NY', \
                'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', \
                'TX', 'UT',	'VT', 'VA',	'WA', 'WV',	'WI', 'WY'
            ]


class ImageForm(forms.ModelForm):
    """
    Form where user records the year and form type to which a sheet belongs 
    """

    class Meta:
        model = Image
        fields = ['year', 'image_type']
    
    def form_valid(self):
        return True


class SheetForm(forms.Form):
    """
    Define form to enter sheet data (year and type)
    """
    
    class Meta:
        model = Sheet
        fields = ['year', 'form_type']


class BreakerForm(forms.Form):
    """
    Class defining form where breaker data are entered


    """
    class Meta:
        model = Breaker
        fields = ['year', 'state', 'county']


class RecordForm(forms.Form):
    """
    Class defining form for entry of single record

    Instantiated with a year and form type
    """

    def __init__(self, year, form_type):
        self.year = year
        self.form_type = form_type

    class Meta:
        model = Record
        fields = ['first_name', 'last_name']
    


  