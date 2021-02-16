"""
FORMS FOR DCDL DATA ENTRY

TO DO:
-Validation methods
"""

from django import forms 
from EntryApp.models import Breaker, Image, Record, Sheet, FormField, CurrentEntry



#=====================================================#
# CHOICES 
#=====================================================#

YEAR_CHOICES = [
    (1960, 1960),
    (1970, 1970),
    (1980, 1980),
    (1990, 1990),
]

IMAGE_TYPE_CHOICES = [
    ("breaker", "Breaker"),
    ("sheet", "Sheet"),
    ("other", "Other"),
]

# TO DO: get names to match actual taxonomy - check w/Katie
FORM_CHOICES = [
    ('short', 'Short'),
    ('long', 'Long'),
]

STATE_LIST = [
                'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', \
                'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', \
                'MI', 'MN', 'MS', 'MO',	'MT', 'NE',	'NV', 'NH',	'NJ', 'NM',	'NY', \
                'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', \
                'TX', 'UT',	'VT', 'VA',	'WA', 'WV',	'WI', 'WY',
            ]

RELP_CHOICES=[
            ('hh_head', 'Head of household'),
            ('wife', 'Wife'),
            ('child', 'Child'),
            ('other_relative', 'Other relative'),
            ('roomer/boarder', 'Roomer, boarder, lodger'),
            ('patient/inmate', 'Patient or inmate'),
            ('other', 'Other not related to head'),
            ]

#================================#
# FORMS FOR DATA ENTRY
#================================#

class ImageForm(forms.Form):
    """
    Form where user records the year and form type to which a sheet belongs 
    """

    year = forms.MultipleChoiceField(
                widget=forms.RadioSelect,
                choices=YEAR_CHOICES, label='Year'
            )
    image_type = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=IMAGE_TYPE_CHOICES, label='Image type')

    # TO DO    
    def form_valid(self, form):
        return True


class BreakerForm(forms.ModelForm):
    """
    Class defining form where breaker data are entered
    NOTE: fields get dynamically defined in views.py based on which year it is
    """
    class Meta:
        model = Breaker
        fields = ['state']

    def form_valid(self):
        return True
        

class SheetForm(forms.ModelForm):
    """
    Define form to enter sheet data (year and type)

    Constructed using a jbid so possible breakers list can be populated
    """

    form_type = forms.ChoiceField(choices=FORM_CHOICES, widget=forms.RadioSelect, label='Form type')
    
    class Meta:
        model = Sheet
        fields = ['num_records']    


#================================#
# DATA MANAGEMENT FORMS
#================================#

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

class ProblemForm(forms.Form):
    '''
    Define form where users can record a problem with a data entry task
    '''

    problem = forms.BooleanField(label="Check here to indicate bad data")
    description = forms.CharField(widget=forms.Textarea, required=False)


#================================#
# BASE CLASSES
#================================#

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


#================================#
# FOR DEV
#================================#

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import Div

import EntryApp.layouts as layouts


class CrispyFormSetHelper(FormHelper):
    '''
    Custom FormHelper for Record formset layout

    This FormHelper applies CSS styling and defines layout.
    TO DO: load custom layouts for each form type
    '''
    def __init__(self, year, form, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method='post'
        self.form_class='form-inline'
        self.label_class = 'sr-only'
        self.layout = layouts.FORM_DICT[year][form]
        self.render_required_fields=True
        self.add_input(Submit("submit", "Submit"))


# class RecordForm(forms.ModelForm):
#     '''
#     Defines record entry form using Record model

#     Note: layout is defined in the formset class. To change approaches so that
#     there is one record per page, override __init__ here and copy in helper 
#     form layout from the formset class.
#     '''

#     class Meta:
#         model = Record
#         fields = [
#             'first_name',
#             'middle_init',
#             'last_name',
#              'age',
#             #  'sex',
#             #  'birth_month',
#             ]

#     def __init__(self, fields, *args, **kwargs):
#         self.Meta.fields = fields
#         super().__init__(*args, **kwargs)