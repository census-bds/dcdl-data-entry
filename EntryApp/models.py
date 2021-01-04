"""
MODELS FOR DCDL DATA ENTRY

TO DO:
-Validation (or do in forms?)
-Nulls and blanks: MAKE SURE SHEETS HAVE BREAKERS
"""

from django.db import models
from django.urls import reverse

#=====================================================#
# CHOICES (BETTER TO DO THIS AS A CONFIG FILE MAYBE)
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
    jbid = models.CharField(max_length=20, default='jbid000')

    # these values will be populated as entry proceeds
    year = models.IntegerField(null=True, choices=YEAR_CHOICES)
    image_type = models.CharField(max_length=8, null=True, choices = IMAGE_TYPE_CHOICES)
    
    # metadata
    is_complete = models.BooleanField(null=True) # need a validation constraint here
    timestamp = models.DateTimeField(null=True)
    problem = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['img_path', 'jbid'], name='unique_img_entry')
        ]

    def __str__(self):
        return f'Image {self.img_path}: {self.year} {self.image_type}'


class Breaker(models.Model):
    """
    Class defining a breaker sheet
    """
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['img', 'jbid'], name='unique_breaker_entry')
        ]

    # required fields
    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    jbid = models.CharField(max_length=7)
    timestamp =  models.DateTimeField(null=True)

    # TO DO: validation for states
    year = models.IntegerField(null=True, choices=YEAR_CHOICES)
    state = models.CharField(max_length=2, null=True)
    county = models.CharField(max_length=30, null=True)
    enum_dist = models.CharField(max_length=30, null=True)
    mcd = models.CharField(max_length=30, null=True)
    tract = models.CharField(max_length=30, null=True)
    place = models.CharField(max_length=30, null=True)
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
    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    breaker = models.ForeignKey(Breaker, on_delete=models.CASCADE)
    jbid = models.CharField(max_length=7) 
    timestamp =  models.DateTimeField(null=True)

    year = models.IntegerField(null=True, choices=YEAR_CHOICES)
    form_type = models.CharField(max_length=200, choices=FORM_CHOICES)

    num_records = models.PositiveIntegerField(verbose_name = 'Number of records', null=True)
    problem = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.img}: {self.form_type}' # FIX THIS


class OtherImage(models.Model):
    '''
    Class defining an image that is neither a breaker nor a sheet

    Attributes: image object, year, free text notes
    '''

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['img', 'jbid'], name='unique_other_entry')
        ]

    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    jbid = models.CharField(max_length=7)
    year = models.PositiveIntegerField(choices=YEAR_CHOICES)
    description = models.TextField(max_length=500)
    timestamp =  models.DateTimeField(null=True)


    def __str__(self):
        return f'{self.img}: OtherImage'


class Record(models.Model):
    """
    Class defining a single record (one person)

    A sheet image contains 1+ records
    """

    # required to uniquely identify the record  
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    page_num = models.PositiveSmallIntegerField(verbose_name='Page number', null=True)
    row_num = models.PositiveSmallIntegerField(verbose_name='Row number', null=True) 
    col_num = models.PositiveSmallIntegerField(verbose_name='Column number', null=True)
    jbid = models.CharField(max_length=7) # change to non-null

    # fields common among all year-forms
    first_name = models.CharField(max_length=50, null=True)
    middle_init = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True)
    age = models.PositiveIntegerField(null=True)
    sex = models.BooleanField(choices=[(0, 'Male'), (1, 'Female')], null=True) # fix this

    # fields that appear in some year-forms but not all
    race = models.CharField(max_length=50, null=True) 
    page_no = models.PositiveIntegerField(null=True)
    line_no = models.PositiveIntegerField(null=True) 
    serial_no = models.IntegerField(null=True)
    block = models.CharField(max_length=50, null=True)
    sample_key_gq = models.CharField(max_length=50, null=True)
    relp = models.CharField(max_length=50, null=True)
    ind = models.CharField(max_length=50, null=True)
    occp = models.CharField(max_length=50, null=True)
    hhincome = models.CharField(max_length=50, null=True)
    educ = models.CharField(max_length=50, null=True)
    citizenship = models.CharField(max_length=50, null=True)
    ancestry = models.CharField(max_length=50, null=True)
    birth_year = models.PositiveIntegerField(null=True)
    birth_month = models.CharField(max_length=15, null=True)
    birth_quarter = models.CharField(max_length=15, null=True)
    total_persons = models.PositiveIntegerField(null=True)

    # entry info
    timestamp =  models.DateTimeField(null=True)
    is_illegible = models.BooleanField(blank=True, null=True)


    def __str__(self):
        return f'Record {self.row_num} {self.jbid} on {self.sheet}: {self.last_name, self.first_name}'

#=====================================================#
# MODELS FOR METADATA AND BACKEND
#=====================================================#

class CurrentEntry(models.Model):

    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    jbid = models.CharField(max_length=20, default='jbid000')
    breaker = models.ForeignKey(Breaker, on_delete=models.CASCADE)
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