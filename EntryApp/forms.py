"""
FORMS FOR DCDL DATA ENTRY

TO DO:
-Validation methods
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

import EntryApp.choices as choices
import EntryApp.layouts as layouts
from EntryApp.models import Breaker, Image, Record, Sheet, FormField, CurrentEntry


#================================#
# FORMS FOR DATA ENTRY
#================================#

class ImageYearForm(forms.Form):

    """
    Form where user records the year to which an image belongs
    """

    year = forms.MultipleChoiceField(
                widget=forms.RadioSelect,
                choices=choices.YEAR_CHOICES,
                label='Year'
            )

    # TO DO
    def form_valid(self, form):
        return True

#-- END form ImageYearForm --#

class ImageTypeForm(forms.Form):

    """
    Form where user records the form type to which an image belongs
    """

    image_type = forms.MultipleChoiceField(
                     widget=forms.RadioSelect,
                     choices=choices.IMAGE_TYPE_CHOICES,
                     label='Image type'
                 )

    # TO DO
    def form_valid(self, form):
        return True

#-- END form ImageTypeForm --#

class ImageForm(forms.Form):
    """
    Form where user records the year and form type to which a sheet belongs
    """

    year = forms.MultipleChoiceField(
                widget=forms.RadioSelect,
                choices=choices.YEAR_CHOICES, label='Year'
            )
    image_type = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=choices.IMAGE_TYPE_CHOICES, label='Image type')

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

    form_type = forms.ChoiceField(choices=choices.FORM_CHOICES, widget=forms.RadioSelect, label='Form type')

    class Meta:
        model = Sheet
        fields = ['num_records']


#================================#
# RECORD FORMS FOR EACH YEAR
#================================#


class RecordForm(forms.ModelForm):
    """
    Define form to enter record data (i.e. individual data)
    """

    # https://stackoverflow.com/questions/3419997/creating-a-dynamic-choice-field

    class Meta:
        model = Record
        exclude = [
            'jbid',
            'timestamp',
            'is_illegible',
        ]
        widgets = {
            'relp_1960': forms.RadioSelect,
            'relp_1970': forms.RadioSelect,
            'relp_1980': forms.RadioSelect,
            'relp_1990': forms.RadioSelect,
            'sex': forms.RadioSelect,
            'race_1960': forms.RadioSelect,
            'race_1970': forms.RadioSelect,
            'race_1980': forms.RadioSelect,
            'race_1990': forms.RadioSelect,
            'birth_quarter': forms.RadioSelect,
            'birth_decade': forms.RadioSelect,
            'birth_year': forms.RadioSelect,
            'marital_status': forms.RadioSelect,
            'age_hundreds': forms.RadioSelect,
            'age_tens': forms.RadioSelect,
            'age_ones': forms.RadioSelect,
            'birth_year_thousands': forms.RadioSelect,
            'birth_year_hundreds': forms.RadioSelect,
            'birth_year_tens': forms.RadioSelect,
            'birth_year_ones': forms.RadioSelect,
            'block_1': forms.RadioSelect,
            'block_2': forms.RadioSelect,
            'block_3': forms.RadioSelect,
            'serial_no_1':forms.RadioSelect,
            'serial_no_2':forms.RadioSelect,
            'serial_no_3':forms.RadioSelect,
            'serial_no_4':forms.RadioSelect,
            'serial_no_5':forms.RadioSelect,
            'serial_no_6':forms.RadioSelect,
            'serial_no_7':forms.RadioSelect,
            'serial_no_8':forms.RadioSelect,
            'serial_no_9':forms.RadioSelect,
            'serial_no_10':forms.RadioSelect,
            'serial_no_11':forms.RadioSelect,
            'total_persons_hundreds': forms.RadioSelect,
            'total_persons_tens': forms.RadioSelect,
            'total_persons_ones': forms.RadioSelect,
        }

    def form_valid(self, form):
        return True



#================================#
# DATA MANAGEMENT FORMS
#================================#

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
        #self.queryset = Breaker.objects.none()



class CrispyFormSetHelper(FormHelper):
    '''
    Custom FormHelper for Record formset layout

    This FormHelper applies CSS styling and defines layout.
    The layout comes from the year and form specified in __init__
    '''
    def __init__(self, year, form, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method='POST'
        self.form_class='form-inline col-8'
        self.label_class = 'sr-only'
        self.layout = layouts.FORM_DICT[year][form]
        self.render_required_fields=True
        self.add_input(Submit("submit", "Submit"))
