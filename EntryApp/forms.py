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


class TestCrispyForm(forms.Form):

    last_name = forms.CharField(max_length=30)
    middle_init = forms.CharField(max_length=2)
    first_name = forms.CharField(max_length=30)
    age = forms.IntegerField(min_value=0, max_value=120)
    relp = forms.ChoiceField(
        choices=[
            ('hh_head', 'Head of household'),
            ('wife', 'Wife'),
            ('child', 'Child'),
            ('other_relative', 'Other relative'),
            ('roomer/boarder', 'Roomer, boarder, lodger'),
            ('patient/inmate', 'Patient or inmate'),
            ('other', 'Other not related to head')
            ],
        widget=forms.RadioSelect
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        
        self.helper.form_class = 'form-inline'
        # self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.label_class = 'sr-only'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Div(
                    'last_name',
                    Div(
                        Div(
                            'first_name',
                            css_class='col-sm-2'
                        ),
                        Div(
                            'middle_init',
                            css_class='col-sm-1'
                        ),
                        css_class='row'
                        ),
                    css_class='col-sm-3'),
                Div(
                    'relp',
                    css_class='col-sm-2'
                ),
                Div(
                    'age',
                    css_class='col-sm-1'
                ),
            css_class='row'),
            Div(
                Submit('submit', 'Add', css_class='btn btn-primary')
                )
        )


class CrispyFormSetHelper(FormHelper):
    '''
    Custom FormHelper for Record formset layout

    This FormHelper applies CSS styling and defines layout.
    TO DO: load custom layouts for each form type
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method='post'
        self.form_class='form-inline'
        self.label_class = 'sr-only'
        self.layout = Layout(
                            Div(
                                Div(
                                    'last_name',
                                    Div(
                                        Div(
                                            'first_name',
                                            css_class='col-sm-1'
                                        ),
                                        Div(
                                            'middle_init',
                                            css_class='col-sm-1'
                                        ),
                                        css_class='row'
                                        ),
                                    css_class='col-sm-1'),
                                # Div(
                                #     'relp',
                                #     css_class='col-sm-1'
                                # ),
                                Div(
                                    'age',
                                    css_class='col-sm-1'
                                ),
                                Div(
                                    'sex',
                                    css_class='col-sm-1'
                                ),
                                Div(
                                    'birth_month',
                                    css_class='col-sm-1'
                                ),
                                # Div(
                                #     'serial_no',
                                #     css_class='col-sm-1'
                                # ),
                                # Div(
                                #     'block',
                                #     css_class='col-sm-1'
                                # ),
                            css_class='row')
                        )
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