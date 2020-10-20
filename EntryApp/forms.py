"""
FORMS FOR DCDL DATA ENTRY

TO DO:
-Validation methods
"""

from django import forms 

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


class BreakerForm(forms.ModelForm):
    """
    Class defining form where breaker data are entered


    """
    class Meta:
        model = Breaker
        fields = ['state', 'county']

    def form_valid(self):
        return True
        

class SheetForm(forms.ModelForm):
    """
    Define form to enter sheet data (year and type)
    """
    
    class Meta:
        model = Sheet
        fields = ['form_type', 'num_records', 'problem']


  