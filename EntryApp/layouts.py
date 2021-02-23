"""
DEFINE LAYOUTS FOR DCDL DATA ENTRY
 Contains the layouts for each form for each year
"""

from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import Div, InlineRadios

LONG_1960 = Layout(
    Div(
        Div(
            Div('page_no', css_class='col-sm-1'),
            Div('line_no', css_class='col-sm-1'),
            Div(InlineRadios('sample_key_gq'), css_class='col-sm-1'),
            Div('last_name', css_class='col-sm-1'),
            Div('first_name', css_class='col-sm-1'),
            Div('middle_init', css_class='col-sm-1'),
            Div(InlineRadios('relp_1960'), css_class='col-sm-1'),
            Div('sex', css_class='col-sm-1'),
            Div(InlineRadios('race_1960'), css_class='col-sm-1'),
            Div(InlineRadios('birth_quarter'), css_class='col-sm-1'),
            Div(InlineRadios('birth_decade'), css_class='col-sm-1'),
            Div(InlineRadios('birth_year'), css_class='col-sm-1'),
            Div(InlineRadios('marital_status'), css_class='col-sm-1'),
        css_class='row'
        ),
        Div(
            Div('street_name', css_class='col-sm-1'),
            Div('house_no', css_class='col-sm-1'),
            Div('apt_no', css_class='col-sm-1'),
        css_class='row'
        ),
    css_class='table-bordered')
)


SHORT_1970 = Layout(
        Div(
            Div(
                'last_name',
                Div(
                    Div(
                        'first_name',
                        css_class='col-sm-10'
                    ),
                    Div(
                        'middle_init',
                        css_class='col-sm-2'
                    ),
                    css_class='row'
                    ),
                css_class='col-sm-3'
                ),
            Div(
                'age',
                css_class='col-sm-1'
            ),
            Div(
                'sex',
                css_class='col-sm-1'
            ),
            Div(
                'exact_birth_month',
                css_class='col-sm-1'
            ),
        css_class='row')
    )

NAME_FIELD_LAYOUT = Div(
    'last_name',
    Div(
        Div('first_name', css_class='col-lg-8 col-md-8 col-sm-8'),
        Div('middle_init', css_class='col-lg-4 col-md-4 col-sm-4'),
        css_class='row'
        ), 
    css_class='col-lg-3 col-md-3 col-sm-3'
    )

LONG_1970 = Layout(
    Div(    
    Div(
        NAME_FIELD_LAYOUT,
        Div('relp_1970', css_class='col-lg-2 col-md-2 col-sm-2'),
        Div('sex', css_class='col-lg-1 col-md-1 col-sm-1'),
        Div(InlineRadios('race_1970'), css_class='col-lg-2 col-md-2 col-sm-2'),
        Div(
            Div('exact_birth_month', css_class='row'),
            Div('exact_birth_year', css_class='row'),
            Div('age', css_class='row'),
        css_class='col-lg-1 col-md-1 col-sm-1'
        ),
        Div(InlineRadios('birth_quarter'), css_class='col-lg-1 col-md-1 col-sm-1'),
        Div('serial_no', css_class='col-lg-1 col-md-1 col-sm-1'),
        Div('block', css_class='col-lg-1 col-md-1 col-sm-1'),
    css_class='row'),
    css_class='table-bordered'
    )
)

FORM_1980 = Layout(
    Div(
        Div('col_num', css_class='row col-lg-11 col-md-11 col-sm-11'),
        Div('last_name', css_class='row col-lg-11 col-md-11 col-sm-11'),
        Div(
            Div('first_name', css_class='col-lg-8 col-md-8 col-sm-8'),
            Div('middle_init', css_class='col-lg-4 col-md-4 col-sm-4'),
            css_class='row'
        ),
        Div('sex', css_class='row'),
        Div('race_1980', css_class='row'),
        Div(
            Div('age', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('exact_birth_year', css_class='col-lg-4 col-md-4 col-sm-4'),
            css_class='row'
        ),
        Div('exact_birth_month', css_class='row col-lg-11 col-md-11 col-sm-11'),
        Div('birth_quarter', css_class='row'),
        Div(
            Div('block', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('serial_no', css_class='col-lg-4 col-md-4 col-sm-4'),
            Div('total_persons', css_class='col-lg-4 col-md-4 col-sm-4'),
            css_class='row'
        ),
    css_class='table-bordered col-lg-4 col-md-4 col-sm-4'
    )
)

FORM_1990 = Layout(
    Div(
        Div('col_num', css_class='row col-lg-11 col-md-11 col-sm-11'),
        Div('last_name', css_class='row col-lg-11 col-md-11 col-sm-11'),
        Div(
            Div('first_name', css_class='col-lg-8 col-md-8 col-sm-8'),
            Div('middle_init', css_class='col-lg-4 col-md-4 col-sm-4'),
            css_class='row'
        ),
        Div('sex', css_class='row'),
        Div('race_1990', css_class='row'),
        Div(
            Div('age', css_class='col-lg-6 col-md-6 col-sm-6'),
            Div('exact_birth_year', css_class='col-lg-6 col-md-6 col-sm-6'),
            css_class='row'
        ),
        Div('serial_no', css_class='row col-lg-10 col-md-10 col-sm-10'),
        Div('marital_status', css_class='row col-lg-10 col-md-10 col-sm-10'),
        Div('total_persons', css_class='row col-lg-10 col-md-10 col-sm-10'),
        css_class='table-bordered col-lg-4 col-md-4 col-sm-4'
    )
)


FORM_DICT = {
    1960: {
        'short': LONG_1960,
        'long': LONG_1960,
    },
    1970: {
        'short': SHORT_1970,
        'long': LONG_1970,
    },
    1980: {
        'short': FORM_1980,
        'long': FORM_1980,
    },
    1990: {
        'short': FORM_1990,
        'long': FORM_1990,
    }
}
