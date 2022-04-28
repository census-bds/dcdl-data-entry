"""
FORMS FOR DCDL DATA ENTRY
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

import EntryApp.choices as choices
import EntryApp.layouts as layouts

from EntryApp.models import Breaker
from EntryApp.models import Household1960
from EntryApp.models import Image
from EntryApp.models import LongForm1990 
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Sheet


#================================#
# FORMS FOR DATA ENTRY
#================================#

# this section is organized in the order of entry, then alphabetically

class ImageForm(forms.ModelForm):
    """
    Model form for images. 
    Custom __init__ identifies images from 1990 reels and longform reels.
    These adjust the choice set for image type.

    Fields shown:
    - image_type, as a radio button
    """

    class Meta:
        model = Image
        fields = ['image_type']
        widgets = {
            'image_type': forms.RadioSelect
        }


    def __init__(self, year, reel_name, *args, **kwargs):
        super(ImageForm, self).__init__(*args, **kwargs)
        
        if year == 1990 and reel_name[6] == '6':
            choice_list = ('longform', '1990 long form')
        
        elif year == 1990 and reel_name[6] != '6':
            choices_list = [c for c in choices.IMAGE_TYPE_CHOICES if c != ('breaker', 'Breaker')]
        
        elif year < 1990:
            choices_list = choices.IMAGE_TYPE_CHOICES

        self.fields.get('image_type').choices = choices_list


class LongForm1990Form(forms.ModelForm):
    """
    Model form for EntryApp.LongForm1990, 
    These are the 1990 long forms, which have employer data

    Fields: do not show the following
    - image foreign key
    - keyer jbid
    - timestamps 
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
    Model form for EntryApp.OtherImage

    Fields: do not show the following
    - image foreign key
    - keyer jbid
    - year (we know this from knowing the reel)
    - timestamps
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


class SheetForm(forms.ModelForm):
    """
    Model form for EntryApp.Sheet model.
    
    Fields specified:
    - # of records, i.e. # of people listed on page
    """

    class Meta:
        model = Sheet
        fields = ['num_records']


class Household1960Form(forms.ModelForm):
    '''
    Model form for EntryApp.Household1960 model

    Fields: do not show
    - image foreign key
    - sheet foreign key
    - keyer jbid
    '''

    class Meta:
        model = Household1960
        exclude = [
            'image',
            'sheet',
            'jbid'
        ]



class RecordForm(forms.ModelForm):
    '''
    Model form for EntryApp.Record model

    Fields: 
    - these are set dynamically by the view with a lookup in EntryApp.FormField
    - we never show:
        - keyer jbid
        - timestamps
        - completion status 
    '''
    
    class Meta:
        model = Record
        exclude = [
            'jbid',
            'timestamp',
            'is_complete',
        ]


#================================#
# DATA MANAGEMENT FORMS
#================================#

class ProblemForm(forms.Form):
    '''
    Generic form for recording a problem with an image.
    These map to fields in EntryApp.Image

    Fields:
    - problem: boolean for presence of problem (checkbox), maps to 
        EntryApp.Image.problem
    - description: text box for description of issue, maps to 
        EntryApp.Image.problem_description 
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
    Subclass for BreakerFormSet so that formset returns no existing data
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


#================================#
# FORM HELPERS
#================================#

class BreakerFormHelper(FormHelper):
    '''
    Custom FormHelper to control order of breaker fields
    '''
    def __init__(self, year, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'POST'
        self.form_class = ''
        self.layout = layouts.BREAKER_FORM_DICT[year]


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