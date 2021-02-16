"""
DEFINE LAYOUTS FOR DCDL DATA ENTRY
 Contains the layouts for each form for each year
"""

from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import Div, InlineRadios



SHORT_1970 = Layout(
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
                    css_class='row')
                )

LONG_1970 = Layout(
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
                        Div(
                            'serial_no',
                            css_class='col-sm-1'
                        ),
                        Div(
                            'block',
                            css_class='col-sm-1'
                        ),
                    css_class='row')
                )


FORM_DICT = {
    1970: {
        'short': SHORT_1970,
        'long': LONG_1970,
    },
}
