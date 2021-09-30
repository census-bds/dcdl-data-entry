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
from EntryApp.models import Breaker
from EntryApp.models import Image
from EntryApp.models import Record
from EntryApp.models import Sheet
from EntryApp.models import OtherImage
from EntryApp.models import LongForm1990 
from EntryApp.models import FormField
from EntryApp.models import CurrentEntry


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


class ImageForm(forms.ModelForm):
    """
    Model form version of the Image form
    """

    class Meta:
        model = Image
        fields = ['image_type']
        widgets = {
            'image_type': forms.RadioSelect
        }


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
    Define form to enter sheet data: # of records
    """

    class Meta:
        model = Sheet
        fields = ['num_records']

class LongForm1990Form(forms.ModelForm):
    """
    Define form to enter data from 1990 long forms w/employer info
    """

    class Meta:
        model = LongForm1990
        exclude = [
            'img',
            'jbid',
            'timestamp',
            'create_date',
            'last_modified',
        ]


class OtherImageForm(forms.ModelForm):
    """
    Define form to capture data about 'other' images where no data entered
    """

    class Meta:
        model = OtherImage
        exclude = [
            'img',
            'jbid',
            'year',
            'timestamp',
            'create_date',
            'last_modified',
        ]


class RecordForm(forms.ModelForm):
    """
    Define form to enter record data (i.e. individual data)
    """
    
    class Meta:
        model = Record
        exclude = [
            'jbid',
            'timestamp',
            'is_illegible',
            'is_complete',
        ]


#================================#
# DATA MANAGEMENT FORMS
#================================#

class ProblemForm(forms.Form):
    '''
    Define form where users can record a problem with a data entry task
    '''

    problem = forms.BooleanField(
        label = "Check here to indicate there's a problem with entered data",
        required = False
    )
    description = forms.CharField(
        widget = forms.Textarea,
        required = False
    )


#================================#
# BASE CLASSES
#================================#

class BaseRecordFormSet(forms.BaseModelFormSet):
    '''
    Subclass for RecordFormSet so that formset returns existing data
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BaseEmptyRecordFormSet(forms.BaseModelFormSet):
    '''
    Subclass for RecordFormSet so that formset returns no existing data
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset =  Record.objects.none()

class BaseBreakerFormSet(forms.BaseModelFormSet):
    '''
    Subclass for BreakerFormSet so that it returns no existing data
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.queryset = Breaker.objects.none()


class RecordFormHelper(FormHelper):
    '''
    Custom FormHelper for Record form layout

    This FormHelper applies CSS styling and defines layout.
    The layout comes from the year and form specified in __init__
    '''
    def __init__(self, year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method='POST'
        self.form_class=''  
        self.label_class = 'sr-only'
        self.layout = layouts.FORM_DICT[year]
        self.render_required_fields=True
        self.form_tag = False


class LongFormHelper(RecordFormHelper):
    '''
    Custom FormHelper for 1990 special form output

    Subclasses the record form helper
    '''
    def __init__(self, year, *args, **kwargs):
        super().__init__(year, *args, **kwargs)
        self.layout = layouts.LONG_FORM_1990


class CrispyFormSetHelper(FormHelper):
    '''
    Custom FormHelper for Record formset layout

    This FormHelper applies CSS styling and defines layout.
    The layout comes from the year and form specified in __init__
    '''
    def __init__(self, year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method='POST'
        self.form_class= ''
        self.layout = layouts.DEV_FORM_DICT[year]
        self.render_required_fields=True
        self.form_tag = False

        self.queryset = Record.objects.none()


class CrispyLongFormHelper(CrispyFormSetHelper):
    '''
    Custom form helper for 1990 special form layout

    Subclasses CrispyFormSetHelper because it's used in the same spot
    '''

    def __init__(self, year, *args, **kwargs):
        super().__init__(year, *args, **kwargs)
        self.layout = layouts.LONG_FORM_1990