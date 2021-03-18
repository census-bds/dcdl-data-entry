"""
MODELS FOR DCDL DATA ENTRY

TO DO:
-Validation (or do in forms?)
"""

from django.db import models
from django.urls import reverse

import EntryApp.choices as choices


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
    ("other", "Other")
]

# TO DO: get names to match actual taxonomy - check w/Katie
FORM_CHOICES = [
    ('short', 'Short'),
    ('long', 'Long')
]

#=====================================================#
# MODELS FOR DATA ENTRY
#=====================================================#

class Image(models.Model):
    """
    Base class for all images.

    Here, we know the filename/path, but need to enter what kind
    of image it is (sheet vs. breaker)
    """

    # we will bulk load DB with all images to enter 
    img_path = models.CharField(max_length=200)
    jbid = models.CharField(
        max_length=20,
        default='jbid000'
    )

    # these values will be populated as entry proceeds
    year = models.IntegerField(null=True)
    image_type = models.CharField(
        max_length=8,
        null=True,
        choices = choices.IMAGE_TYPE_CHOICES
    )
    
    # metadata
    is_complete = models.BooleanField(null=True) # need a validation constraint here
    timestamp = models.DateTimeField(null=True)
    problem = models.BooleanField(default=False)
    prob_description = models.TextField(
        verbose_name="Please describe the problem.",
        null=True
    )
    flagged_view = models.CharField(max_length=30, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['img_path', 'jbid',],
                name='unique_img_entry'
            )
        ]

    def __str__(self):
        return f'Image {self.img_path}: {self.year} {self.image_type}'


class Breaker(models.Model):
    """
    Class defining a breaker sheet
    """
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['img', 'jbid'],
                name='unique_breaker_entry'
            )
        ]

    # required fields
    img = models.ForeignKey(
        Image,
        on_delete=models.CASCADE
    )
    jbid = models.CharField(max_length=7, default='jbid000')
    timestamp =  models.DateTimeField(null=True)
    problem = models.BooleanField(default=False)

    # TO DO: validation for states
    year = models.IntegerField(
        null=True,
        choices=choices.YEAR_CHOICES[:3]
    ) 
    # ^ remove 1990 as option because that census did not include breakers
    state = models.CharField(
        max_length=2,
        null=True
    )
    county = models.CharField(
        max_length=30,
        null=True
    )
    enumeration_district = models.CharField(
        max_length=30,
        null=True
    )
    mcd = models.CharField(
        max_length=30,
        null=True
    )
    tract = models.CharField(
        max_length=30,
        null=True
    )
    place = models.CharField(
        max_length=30,
        null=True
    )
    smsa = models.CharField(max_length=30, null=True)
    

    def __str__(self):
        return f'Breaker {self.img} from {self.jbid}'


class Sheet(models.Model):
    """
    Class defining a record sheet 
    
    Attributes: image objects, year, form_type, breaker object,
                ???
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['img', 'jbid'], name='unique_sheet_entry')
        ]

    # required fields
    img = models.ForeignKey(
        Image,
        on_delete=models.CASCADE
    )
    breaker = models.ForeignKey(
        Breaker,
        on_delete=models.CASCADE
    )
    jbid = models.CharField(max_length=7, default='jbid000') 

    # auto-filled, not required
    timestamp =  models.DateTimeField(null=True)
    year = models.IntegerField(
        null=True,
        choices=choices.YEAR_CHOICES
    )
    problem = models.BooleanField(default=False)

    # for entry
    form_type = models.CharField(max_length=200, choices=choices.FORM_CHOICES)
    num_records = models.PositiveIntegerField(
        verbose_name = 'Number of records',
        null=True
    )

    def __str__(self):
        return f'{self.img}: {self.form_type}' # FIX THIS


class OtherImage(models.Model):
    '''
    Class defining an image that is neither a breaker nor a sheet

    Attributes: image object, year, free text notes
    '''

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['img', 'jbid'],
                name='unique_other_entry'
            )
        ]

    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    jbid = models.CharField(max_length=7, default='jbid000')
    year = models.PositiveIntegerField(choices=choices.YEAR_CHOICES)
    description = models.TextField(max_length=500)
    timestamp =  models.DateTimeField(null=True)
    problem = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.img}: OtherImage'


class Record(models.Model):
    """
    Class defining a single record (one person)

    A sheet image contains 1+ records
    """

    # required to uniquely identify the record  
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    page_num = models.PositiveSmallIntegerField(
        verbose_name='Page number',
        null=True
    )
    row_num = models.PositiveIntegerField(verbose_name='Row number', null=True) 
    col_num = models.PositiveIntegerField(
            verbose_name='Column number',
            null=True
        )
    jbid = models.CharField(max_length=7, default='jbid000') 

    # fields common among all year-forms
    first_name = models.CharField(max_length=50, null=True)
    middle_init = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True)
    age = models.PositiveIntegerField(null=True)
    sex = models.CharField(
            choices=choices.SEX_CHOICES,
            max_length=50,
            blank=False,
            default=choices.SEX_CHOICES[0],
            null=True
        )

    # fields that appear in some year-forms but not all
    page_no = models.PositiveIntegerField(null=True)
    line_no = models.PositiveIntegerField(
            null=True,
            verbose_name="Line number"
        ) 
    serial_no = models.IntegerField(null=True, verbose_name="Serial number")
    do_id = models.IntegerField(null=True, verbose_name="DO ID")
    block = models.CharField(max_length=50, null=True)
    sample_key_gq = models.CharField(
            max_length=50,
            blank=False,
            default=choices.SAMPLE_GQ_CHOICES[0],
            null=True,
            choices=choices.SAMPLE_GQ_CHOICES,
            verbose_name="Sample key"
        )
    street_name = models.CharField(max_length=50, null=True)
    house_no = models.IntegerField(null=True, verbose_name="House number")
    apt_no = models.IntegerField(null=True, verbose_name="Apartment number")

    # relp options vary by year     
    relp_1960 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RELP_CHOICES_1960[0],
            null=True,
            choices=choices.RELP_CHOICES_1960,
            verbose_name="Relationship to household head"        
        )
    relp_1970 = models.CharField(
            max_length=50,
            blank=False,
                    default=choices.RELP_CHOICES_1970[0],
            null=True,
            choices=choices.RELP_CHOICES_1970,
            verbose_name="Relationship to household head"        
        )
    relp_1980 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RELP_CHOICES_1980[0],
            null=True,
            choices=choices.RELP_CHOICES_1980,
            verbose_name="Relationship to household head"        
        )
    relp_1990 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RELP_CHOICES_1990[0],
            null=True,
            choices=choices.RELP_CHOICES_1990,
            verbose_name="Relationship to household head"        
        )
    race_1960 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RACE_CHOICES_1960[0],
            null=True,
            choices=choices.RACE_CHOICES_1960,
            verbose_name="Race"
        ) 
    race_1970 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RACE_CHOICES_1970[0],
            null=True,
            choices=choices.RACE_CHOICES_1970,
            verbose_name="Race"
        ) 
    race_1980 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RACE_CHOICES_1980[0],
            null=True,
            choices=choices.RACE_CHOICES_1980,
            verbose_name="Race"
        ) 
    race_1990 = models.CharField(
            max_length=50,
            blank=False,
            default=choices.RACE_CHOICES_1990[0],
            null=True,
            choices=choices.RACE_CHOICES_1990,
            verbose_name="Race"
        )     
    exact_birth_year = models.PositiveIntegerField(
        null=True,
        verbose_name='Year of birth'
        )
    exact_birth_month = models.CharField(
        max_length=15,
        null=True,
        verbose_name='Month of birth'
        )
    birth_year = models.CharField(
            max_length=10,
            blank=False,
            default=choices.SINGLE_DIGIT_CHOICES[0],
            null=True,
            choices=choices.SINGLE_DIGIT_CHOICES,
            verbose_name="Specific year of birth"
        )
    birth_quarter = models.CharField(
            max_length=15,
            blank=False,
            default=choices.BIRTH_QUARTER_CHOICES[0],
            null=True,
            choices=choices.BIRTH_QUARTER_CHOICES,
            verbose_name="Month of birth"
        )
    birth_decade = models.CharField(
            max_length=10,
            blank=False,
            default=choices.BIRTH_DECADE_CHOICES[0],
            null=True,
            choices=choices.BIRTH_DECADE_CHOICES,
            verbose_name="Decade of birth"
        )

    marital_status = models.CharField(
            max_length=50,
            blank=False,
            default=choices.MARITAL_STATUS_CHOICES[0],
            null=False,
            choices=choices.MARITAL_STATUS_CHOICES
        )

    ind = models.CharField(
        max_length=50,
        null=True,
        verbose_name='Industry'
        )
    occp = models.CharField(
        max_length=50,
        null=True,
        verbose_name='Occupation'
        )

    total_persons = models.PositiveIntegerField(null=True)

    # bubble fields


    age_hundreds = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    age_tens = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    age_ones = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )

    birth_year_thousands = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    birth_year_hundreds = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    birth_year_tens = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    birth_year_ones = models.CharField(
        null=True,
        blank=False,
        max_length=10,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )

    block_1 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    block_2 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    block_3 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )


    serial_no_1 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_2 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_2 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_3 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_4 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_5 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_6 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_7 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_8 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_9 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_10 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    serial_no_11 = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )

    total_persons_hundreds = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    total_persons_tens = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )
    total_persons_ones = models.CharField(
        null=True,
        blank=False,
        max_length=2,
        verbose_name="",
        choices=choices.SINGLE_DIGIT_CHOICES,
        default=choices.SINGLE_DIGIT_CHOICES[0]
    )

    # entry info
    timestamp =  models.DateTimeField(null=True)

    def __str__(self):
        return f'Record {self.row_num} {self.jbid} on {self.sheet}: {self.last_name, self.first_name}'

#=====================================================#
# MODELS FOR METADATA AND BACKEND
#=====================================================#

class CurrentEntry(models.Model):

    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    jbid = models.CharField(max_length=20, default='jbid000')
    breaker = models.ForeignKey(Breaker, on_delete=models.SET_NULL, null=True)
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'CurrentEntry: {self.jbid} entering {self.img}'

    def print_breaker_img(self):
        return f'CurrentEntry breaker img is {self.breaker_img}'


class FormField(models.Model):
    """
    Class to track form x field metadata, i.e. which fields are in which forms

    Users never interact with this model directly, but the app uses it to
    look up which fields to serve the user when they are entering data
    """

    year = models.FloatField()
    form_type = models.CharField(max_length=200, choices=FORM_CHOICES)     
    field_name = models.CharField(max_length=50)

    def __str__(self):
        return f'FormField {self.year} {self.form_type}: {self.field_name}'