"""
FORMS FOR DCDL DATA ENTRY

TO DO:
-Validation methods
"""

from django import forms 
from EntryApp.models import Breaker, Image, Record, Sheet, FormField, CurrentEntry

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
    
    def form_valid(self, form):
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

    Constructed using a jbid so possible breakers list can be populated
    """
    
    class Meta:
        model = Sheet
        fields = ['form_type', 'num_records', 'problem']

    breaker_choice = forms.ChoiceField(label='Select a different breaker:')

    def __init__(self, jbid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(b.pk, str(b.year)+ ' ' + b.county + ' ' + b.img.img_path) for b in Breaker.objects.filter(jbid=jbid)]
        self.fields['breaker_choice'].choices = choices
        self.fields['breaker_choice'].initial = CurrentEntry.objects.get(jbid=jbid).breaker


class BaseRecordFormSet(forms.BaseModelFormSet):
    '''
    Subclass for RecordFormSet so that formset returns no existing data
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Record.objects.none()


class BaseBreakerFormSet(forms.BaseModelFormSet):
    '''
    Subclass for BreakerFormSet so that it returns no existing data
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Breaker.objects.none()


class ExportForm(forms.Form):
    '''
    Define form where users can export existing records to csv to inspect
    '''
    
    tables = {
        1: {'label': 'Image', 'model': Image},
        2: {'label': 'Sheet', 'model': Sheet},
        3: {'label': 'Breaker', 'model': Breaker},
        4: {'label': 'Record', 'model': Record},
    }
    choices = [(t[0], t[1]['label']) for t in tables.items()]
    table_choice = forms.ChoiceField(label='Choose table to export', \
        choices=choices)