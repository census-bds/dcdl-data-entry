#=====================================================#
# DEFINE CHOICES FOR ALL DATA ENTRY FIELDS
#=====================================================#

YEAR_CHOICES = [
    (1960, 1960),
    (1970, 1970),
    (1980, 1980),
    (1990, 1990),
]

IMAGE_TYPE_BREAKER = "breaker"
IMAGE_TYPE_SHEET = "sheet"
IMAGE_TYPE_OTHER = "other"
IMAGE_TYPE_CHOICES = [
    ( IMAGE_TYPE_BREAKER, "Breaker" ),
    ( IMAGE_TYPE_SHEET, "Sheet" ),
    ( IMAGE_TYPE_OTHER, "Other"),
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

#================================#
# FIELD-LEVEL CHOICES
#================================#

SAMPLE_GQ_CHOICES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('GQ', 'GQ'),
]

SEX_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
]

BIRTH_QUARTER_CHOICES = [
    ('Jan-Mar', 'Jan-Mar'),
    ('Apr-June', 'Apr-June'),
    ('July-Sept', 'July-Sept'),
    ('Oct-Dec', 'Jan-Mar'),
]

SINGLE_DIGIT_CHOICES = [(str(x), str(x)) for x in list(range(1,10))]

BIRTH_DECADE_CHOICES = [
    ('1850', '185-'),
    ('1860', '186-'),
    ('1870', '187-'),
    ('1880', '188-'),
    ('1890', '189-'),
    ('1900', '190-'),
    ('1910', '191-'),
    ('1920', '192-'),
    ('1930', '193-'),
    ('1940', '194-'),
    ('1950', '195-'),
    ('1960', '196-')
]

BIRTH_CENTURY_CHOICES = [
    ('8', '8'),
    ('9', '9'),
]

BIRTH_MILLENIUM_CHOICES = [
    ('1', '1')
]

MARITAL_STATUS_CHOICES = [
    ('Married', 'Married'),
    ('Widowed', 'Widowed'),
    ('Divorced', 'Divorced'),
    ('Separated', 'Separated'),
    ('Never married', 'Never married')
]

RELP_CHOICES_1960 = [
            ('hh_head', 'Head of household'),
            ('spouse', 'Wife'),
            ('child', 'Child'),
            ('other_relative', 'Other relative'),
            ('roomer/boarder', 'Roomer, boarder, lodger'),
            ('patient/inmate', 'Patient or inmate'),
            ('other', 'Other not related to head'),
    ]


RELP_CHOICES_1970 = [
            ('hh_head', 'Head of household'),
            ('spouse', 'Wife of head'),
            ('child', 'Son or daughter of head'),
            ('other_relative', 'Other relative'),
            ('roomer/boarder', 'Roomer, boarder, lodger'),
            ('patient/inmate', 'Patient or inmate'),
            ('other', 'Other not related to head'),
    ]

RELP_CHOICES_1980 = [
            ('spouse', 'Husband/wife'),
            ('child', 'Son/daughter'),
            ('sibling', 'Brother/sister'),
            ('parent', 'Father/mother'),
            ('other_relative', 'Other relative'),
            ('roomer/boarder', 'Roomer, boarder'),
            ('partner/roommate', 'Partner, roommate'),
            ('paid_employee', 'Paid employee'),
            ('other', 'Other nonrelative'),
    ]

RELP_CHOICES_1990 = [
            ('spouse', 'Husband/wife'),
            ('child', 'Son/daughter'),
            ('stepchild', 'Stepson/stepdaughter'),
            ('sibling', 'Brother/sister'),
            ('parent', 'Father/mother'),
            ('grandchild', 'Grandchild'),
            ('other_relative', 'Other relative'),
            ('roomer/boarder/foster', 'Roomer, boarder, or foster child'),
            ('housemate/roommate', 'Housemate, roommate'),
            ('unmarried_partner', 'Unmarried partner'),
            ('other', 'Other nonrelative'),
    ]

RELP_CHOICES = {
    '1960': RELP_CHOICES_1960,
    '1970': RELP_CHOICES_1970,
    '1980': RELP_CHOICES_1980,
    '1990': RELP_CHOICES_1990,
}



RACE_CHOICES_1960 = [
    ('White', 'White'),
    ('Negro', 'Negro'),
    ('American Indian', 'American Indian'),
    ('Japanese', 'Japanese'),
    ('Chinese', 'Chinese'),
    ('Filipino', 'Filipino'),
    ('Other', 'Other'),
]

RACE_CHOICES_1970 = [
    ('White', 'White'),
    ('Negro or Black', 'Negro or Black'),
    ('Indian (Amer.)', 'Indian (Amer.)'),
    ('Japanese', 'Japanese'),
    ('Chinese', 'Chinese'),
    ('Filipino', 'Filipino'),
    ('Hawaiian', 'Hawaiian'),
    ('Korean', 'Korean'),
    ('Other', 'Other'),
]

RACE_CHOICES_1980 = [
    ('White', 'White'),
    ('Black or Negro', 'Black or Negro'),
    ('Japanese', 'Japanese'),
    ('Chinese', 'Chinese'),
    ('Filipino', 'Filipino'),
    ('Korean', 'Korean'),
    ('Vietnamese', 'Vietnamese'),
    ('Indian (Amer.)', 'Indian (Amer.)'),
    ('Asian Indian', 'Asian Indian'),
    ('Hawaiian', 'Hawaiian'),
    ('Guamanian', 'Guamanian'),
    ('Samoan', 'Samoan'),
    ('Eskimo', 'Eskimo'),
    ('Aleut', 'Aleut'),
    ('Other', 'Other'),
]

RACE_CHOICES_1990 = [
    ('White', 'White'),
    ('Black or Negro', 'Black or Negro'),
    ('Indian (Amer.)', 'Indian (Amer.)'),
    ('Eskimo', 'Eskimo'),
    ('Aleut', 'Aleut'),
    ('Chinese', 'Chinese'),
    ('Japanese', 'Japanese'),
    ('Filipino', 'Filipino'),
    ('Asian Indian', 'Asian Indian'),
    ('Hawaiian', 'Hawaiian'),
    ('Samoan', 'Samoan'),
    ('Korean', 'Korean'),
    ('Guamanian', 'Guamanian'),
    ('Vietnamese', 'Vietnamese'),
    ('Other API', 'Other API'),
]
