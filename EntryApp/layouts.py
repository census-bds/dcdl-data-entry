"""
DEFINE LAYOUTS FOR DCDL DATA ENTRY
Contains the layouts for each form for each year. These layouts get imported
into forms.py into an attribute of the crispy form FormHelper class
corresponding to each form. Note the dictionary at the bottom mapping each 
Layout to a year.

CSS classes referenced here are implemented in style blocks in the HTML files.
This is not ideal, but it worked without being overridden by Bootstrap defaults.
"""

from crispy_forms.layout import Field
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import Div 
from crispy_forms.bootstrap import InlineRadios


#================================#
# RECORD LAYOUTS
#================================#

FORM_1960 = Layout(
    Div(
        Field('page_no', css_class='numberinput-small'), # need to apply the css to the *input* not div
        Field('line_no', css_class='numberinput-small'),
        Field(InlineRadios('sample_key_gq')),
        Field('last_name'),
        Field('first_name'),
        Field('race_writein'),
        Field('middle_init', css_class='textinput-small'),
        Field('suffix', css_class='textinput-small'),
        css_id = 'form-row-div',
        css_class='form-inline form-inline-nowrap',
    )
)


FORM_1970 = Layout(
    Div(
        Field('line_no', css_class='textinput-small'),
        Div(
            Div(
                Field('last_name'),
                Field('suffix', css_class='textinput-small'),
                css_id='form-1970-last-name-suffix'
            ),
            Div(
                Field('first_name'),
                Field('middle_init', css_class='textinput-small'),
                css_id="form-1970-first-name-middle-init"
            ),
            css_id='form-1970-names-div'
        ),
        Field('relp_writein'),
        Field('race_writein'),
        Div(
            Field('age'),
            css_id="form-1970-age-block"
        ),
        Div(
        HTML("<p><b>Block</b></p><br>"),
            Field('block_1'),
            Field('block_2'),
            Field('block_3'),
            css_id="form-1970-block-radios"
        ),
        Div(
            HTML("<p><b>Serial no</b></p><br>"),
            Field('serial_no_1'),
            Field('serial_no_2'),
            Field('serial_no_3'),
            css_id='form-1970-serial-radios'
        ),
        css_id = 'form-row-div',
        css_class='form-inline form-inline-nowrap',
    )
)

FORM_1980 = Layout(
   Div(
        Field('col_no'),
        Field('last_name'),
        Div(
            Field('first_name'),
            Field('middle_init', css_class='textinput-small'),
            Field('suffix', css_class='textinput-small'),
            css_id='form-1980-first-name-middle-init'
        ),
        Field('relp_writein'),
        Field('race_writein'),
        Div(
            Div(
                Field('age'),
            ),
        ),
        Field('block'),
        Div(
            Div('block_1', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('block_2', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('block_3', css_class='col-lg-4 col-md-4 col-sm-4'),
            css_class="row"
        ),
        Field('serial_no'),
        Div(
            Div('serial_no_1', css_class='col-lg-3 col-md-3 col-sm-3'),
            Div('serial_no_2', css_class='col-lg-3 col-md-3 col-sm-3'),
            Div('serial_no_3', css_class='col-lg-3 col-md-3 col-sm-3'),
            Div('serial_no_4', css_class='col-lg-3 col-md-3 col-sm-3'),
            css_class='row'
        ),
        Field('total_persons'),
    css_class='form-inline form-column'
    )    
)

FORM_1990 = Layout(
    Div(
        Field('col_no'),
        Field('last_name'),
        Div(
            Field('first_name'),
            Field('middle_init', css_class='textinput-small'),
            Field('suffix', css_class='textinput-small'),
            css_id='form-1990-first-name-middle-init'
        ),
        Field('relp_writein'),
        Field('tribe_writein'),
        Field('race_writein'),
        Field('total_persons'),
        Div(
            Field('serial_no'),
            Div(
                Div('serial_no_1', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_2', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_3', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_4', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_5', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_6', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_7', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_8', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_9', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_10', css_class='col-lg-1 col-md-1 col-sm-1'),
                Div('serial_no_11', css_class='col-lg-1 col-md-1 col-sm-1'),
                css_class="row"
            )
        ),
        css_class='form-inline form-column'
    )
)

LONG_FORM_1990 = Layout(
    Div(
        Div('employer', css_class='row'),
        Div('industry', css_class='row'),
        Div('industry_category', css_class='row'),
        Div('occupation', css_class='row'),
        Div('occupation_detail', css_class='row'),
        css_class = 'form-inline form-column'
    )
)


RECORD_FORM_DICT = {
    1960: FORM_1960,
    1970: FORM_1970,
    1980: FORM_1980,
    1990: FORM_1990
    }

#================================#
# RECORD LAYOUTS IN DEVELOPMENT
#================================#

CRISPY_FORM_1960 = FORM_1960
CRISPY_FORM_1970 = FORM_1970
CRISPY_FORM_1980 = FORM_1980
CRISPY_FORM_1990 = FORM_1990


DEV_FORM_DICT = {
    1960: CRISPY_FORM_1960,
    1970: CRISPY_FORM_1970,
    1980: CRISPY_FORM_1980,
    1990: CRISPY_FORM_1990,
}

#================================#
# BREAKER LAYOUTS
#================================#


BREAKER_FORM_1980 = Layout(
    Div(
        Field('enumeration_district'),
        Field('county'),
        Field('mcd'),
        Field('place'),
        Field('tract'),
        Field('smsa'),
        css_class = 'form-inline form-column'
    )
)

BREAKER_FORM_1970 = Layout(
    Div(
        Field('county'),
        Field('enumeration_district'),
        css_class = 'form-inline'
    )
)

BREAKER_FORM_1960 = Layout(
    Div(
        Field('enumeration_district')
    )
)

BREAKER_FORM_DICT = {
    1980: BREAKER_FORM_1980,
    1970: BREAKER_FORM_1970,
    1960: BREAKER_FORM_1960
}

#================================#
# SHEET LAYOUT
#================================#

SHEET_1960 = Layout(
    Div(
        Field('num_records'),
        Field('hard_to_read'),
        Div(
            Field('address_one'),
            Field('address_two'),
            css_id="household-1960-address-div",
            css_class="row"
            ),
        Div(
            Div(
                Field(('sample_key_one')),
                Field(('sample_key_two')),
                Field(('sample_key_three')),
                Field(('sample_key_four')),
                # css_id = 'household-1960-radios'
            ),
            Div(
                Field('house_number_one', css_class='numberinput-small'),
                Field('house_number_two', css_class='numberinput-small'),
                Field('house_number_three', css_class='numberinput-small'),
                Field('house_number_four', css_class='numberinput-small'),
                # css_id = 'household-1960-house-number'
            ),
            Div(
                Field('apt_number_one', css_class='numberinput-small'),
                Field('apt_number_two', css_class='numberinput-small'),
                Field('apt_number_three', css_class='numberinput-small'),
                Field('apt_number_four', css_class='numberinput-small'),
                # css_id = 'household-1960-apt_number'
            ),
            css_id = 'household-1960-inputs',
            css_class="row"
        ),
    )
)

SHEET_1970 = Layout(
    Div(
        Field('num_records')
    )
)

SHEET_1980 = Layout(
    Div(
        Field('num_records')
    )
)

SHEET_1990 = Layout(
    Div(
        Field('num_records')
    )
)

SHEET_FORM_DICT = {
    1960: SHEET_1960,
    1970: SHEET_1970,
    1980: SHEET_1980,
    1990: SHEET_1990,
}