"""
DEFINE LAYOUTS FOR DCDL DATA ENTRY
 Contains the layouts for each form for each year
"""

from crispy_forms.layout import Field
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import Div 
from crispy_forms.bootstrap import InlineRadios


#================================#
# CURRENT LAYOUTS
#================================#

FORM_1960 = Layout(
    Div(
        Field('page_no', css_class='numberinput-small'), # need to apply the css to the *input* not div
        Field('line_no', css_class='numberinput-small'),
        Field(InlineRadios('sample_key_gq')),
        Field('last_name'),
        Field('first_name'),
        Field('middle_init', css_class='textinput-small'),
        Field('suffix', css_class='textinput-small'),
        Field(InlineRadios('relp_1960')),
        Field('sex'),
        Field(InlineRadios('race_1960')),
        Field(Div('birth_quarter')),
        Field(InlineRadios('birth_decade')),
        Field(InlineRadios('birth_year')),
        Field(InlineRadios('marital_status')),
        Field('street_name'),
        Field('house_no', css_class='numberinput-small'),
        Field('apt_no', css_class='numberinput-small'),
        css_id = 'form-row-div',
        css_class='form-inline form-inline-nowrap',
    )
)


FORM_1970 = Layout(
    Div(
        Div(
            Field('last_name'),
            Div(
                Field('first_name'),
                Field('middle_init', css_class='textinput-small'),
                Field('suffix', css_class='textinput-small'),
                css_id="form-1970-first-name-middle-init"
            ),
            css_id='form-1970-names-div'
        ),
        Field('relp_1970'),
        Field('sex'),
        Field(InlineRadios('race_1970')),
        Div(
            Field('exact_birth_month'),
            Field('exact_birth_year'),
            Field('age'),
            css_id="form-1970-age-block"
        ),
        Field('birth_quarter'),
        Field('birth_decade'),
        Field('birth_year'),
        Field('serial_no'),
        Field('block'),
        css_id = 'form-row-div',
        css_class='form-inline form-inline-nowrap',
    )
)

FORM_1980 = Layout(
   Div(
        Field('col_num'),
        Field('last_name'),
        Div(
            Field('first_name'),
            Field('middle_init', css_class='textinput-small'),
            Field('suffix', css_class='textinput-small'),
            css_id='form-1980-first-name-middle-init'
        ),
        Div(InlineRadios('sex'), css_id='form-1980-sex-radios'),
        Div('race_1980', css_id='form-1980-race-radios'),
        Div(
            Div(
                Field('age'),
                Field('exact_birth_month'),
                Div('birth_quarter', css_id='race-1980-vertical-radios'),
            ),
            Field('exact_birth_year', css_class='row'),
            Div(
                Div(InlineRadios('birth_year_thousands'), css_class='col-lg-3 col-md-3 col-sm-3'),
                Div(InlineRadios('birth_year_hundreds'), css_class='col-lg-3 col-md-3 col-sm-3'),
                Div(InlineRadios('birth_year_tens'), css_class='col-lg-3 col-md-3 col-sm-3'),
                Div(InlineRadios('birth_year_ones'), css_class='col-lg-3 col-md-3 col-sm-3'),
                css_class='row'
            )
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
        Div(
            Div('total_persons_hundreds', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('total_persons_tens', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('total_persons_ones', css_class='col-lg-4 col-md-4 col-sm-4'),
            css_class='row'
        ),
    css_class='form-inline form-column'
    )    
)

FORM_1990 = Layout(
    Div(
        Field('col_num'),
        Field('last_name'),
        Div(
            Field('first_name'),
            Field('middle_init', css_class='textinput-small'),
            Field('suffix', css_class='textinput-small'),
            css_id='form-1990-first-name-middle-init'
        ),
        Div('sex', css_id='form-1990-sex-radios'),
        Div('race_1990', css_id='form-1990-race-radios'),
        Div(
            Field('age', css_class='numberinput-small'),
            Div(
                Div('age_hundreds', css_class='col-lg-3 col-md-3 col-sm-3'),
                Div('age_tens', css_class='col-lg-3 col-md-3 col-sm-3'),
                Div('age_ones', css_class='col-lg-3 col-md-3 col-sm-3'),
                css_class='row'
            ),
            css_class='col-lg-6 col-md-6 col-sm-6'
        ),
        Div(
            Field('exact_birth_year', css_class='numberinput-small'),
                Div(
                    Div('birth_year_thousands', css_class='col-lg-3 col-md-3 col-sm-3'),
                    Div('birth_year_hundreds', css_class='col-lg-3 col-md-3 col-sm-3'),
                    Div('birth_year_tens', css_class='col-lg-3 col-md-3 col-sm-3'),
                    Div('birth_year_ones', css_class='col-lg-3 col-md-3 col-sm-3'),
                    css_class='row'
                ),
            css_class='col-lg-6 col-md-6 col-sm-6'
        ),
        Div(
            Field('total_persons', css_class='numberinput-small'), 
            Div(
                Div('total_persons_tens', css_class='col-lg-3 col-md-3 col-sm-3'),
                Div('total_persons_ones', css_class='col-lg-3 col-md-3 col-sm-3'),
                css_class='row'
            )
        ),
        Div(
            Field('serial_no'),
            Field('do_id'),
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
        Div(
            Field('serial_no'),
            Field('person_no'),
            css_class='row'
        ),
        Div('employer', css_class='row'),
        Div('industry', css_class='row'),
        Div('industry_category', css_class='row'),
        Div('occupation', css_class='row'),
        Div('occupation_detail', css_class='row'),
        css_class = 'form-inline form-column'
    )
)


FORM_DICT = {
    1960: FORM_1960,
    1970: FORM_1970,
    1980: FORM_1980,
    1990: FORM_1990
    }

#================================#
# LAYOUTS IN DEVELOPMENT
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
