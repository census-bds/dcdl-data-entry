"""
MODELS FOR DCDL DATA ENTRY

TO DO:
-FilePath field type
-Validation
-Nulls and blanks
-keys
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
    ("sheet", "Sheet")
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

    Here, we know the filename/path, but need to en ter what kind
    of image it is (sheet vs. breaker)
    """

    # we will bulk load DB with all images to enter 
    img_path = models.CharField(max_length=200)
    # jbid = models.CharField(max_length=20)

    # these values will be populated as entry proceeds
    year = models.IntegerField(null=True, choices=YEAR_CHOICES)
    image_type = models.CharField(max_length=8, null=True, choices = IMAGE_TYPE_CHOICES)
    
    # metadata
    is_complete = models.BooleanField(null=True)
    date_complete = models.DateTimeField(null=True)


    def __str__(self):
        return f'Image {self.img_path}: {self.year} {self.image_type}'

    def get_absolute_url(self):
        return reverse('image', kwargs={'pk': self.pk})
    

class Sheet(models.Model):
    """
    Class defining a record sheet 
    
    Attributes: image_id, year, form_type, breaker_id,
                ???
    """

    img_path = models.ForeignKey(Image, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, choices=YEAR_CHOICES)

    form_type = models.CharField(max_length=200, choices=FORM_CHOICES)
    breaker_id = models.CharField(max_length=200)

    def __str__(self):
        return f'Image {self.img_path}: {self.year} {self.form_type}'

    @classmethod
    def list_records(cls):
        """
        List records associated with this sheet image
        """
        return Record.objects.filter(image_id=cls.img_path)


class Breaker(models.Model):
    """
    Class defining a breaker sheet (subclass of image)
    """
    
    img_path = models.ForeignKey(Image, on_delete=models.CASCADE)
    year = models.IntegerField(null=True, choices=YEAR_CHOICES)

    # geography fields
    # TO DO: fix types and do validation
    state = models.CharField(max_length=2, null=True) # valid list of states
    county = models.CharField(max_length=30, null=True)
    enum_dist = models.CharField(max_length=30, null=True)
    mcd = models.CharField(max_length=30, null=True)
    tract = models.CharField(max_length=30, null=True)
    place = models.CharField(max_length=30, null=True)
    smsa = models.CharField(max_length=30, null=True)
    large_do_ed = models.CharField(max_length=30, null=True) #TO DO: ask Katie what this is
    
    def __str__(self):
        return f'Breaker {self.img_path} from {self.year}'

    @classmethod
    def get_related_sheets(cls):
        """
        Return list of Sheets associated with this instance of breaker
        """
        pass


class Record(models.Model):
    """
    Class defining a single record (one person)

    A sheet image contains 1+ records
    """

    # link to the image 
    record_id = models.PositiveSmallIntegerField(primary_key=True) # this is row (or col)
    img_path = models.ForeignKey(Sheet, on_delete=models.CASCADE)

    # fields common among all year-forms
    first_name = models.CharField(max_length=50, null=True)
    middle_init = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True)
    age = models.PositiveIntegerField(null=True)
    sex = models.BooleanField(choices=[(0, 'Male'), (1, 'Female')], null=True) # fix this

    # fields that appear in some year-forms but not all
    race = models.CharField(max_length=50, null=True) 
    page_no = models.PositiveIntegerField(null=True)
    line_no = models.PositiveIntegerField(null=True) # this may be row or col no
    serial_no = models.IntegerField(null=True)
    block = models.CharField(max_length=50, null=True)
    sample_key_gq = models.CharField(max_length=50, null=True)
    relp = models.CharField(max_length=50, null=True)
    ind = models.CharField(max_length=50, null=True)
    occp = models.CharField(max_length=50, null=True)
    birth_year = models.PositiveIntegerField(null=True)
    birth_month = models.CharField(max_length=15, null=True)
    total_persons = models.PositiveIntegerField(null=True)

    # entry info
    user_id = models.CharField(max_length=50, null=True)
    entry_time = models.DateTimeField()
    is_illegible = models.BooleanField(blank=True, null=True)


    def __str__(self):
        return f'Record {self.record_id}: {self.last_name, self.first_name}'

#=====================================================#
# MODELS FOR METADATA AND BACKEND
#=====================================================#


class Conflict(models.Model):
    """
    Class to track records that conflict after double-entry

    Tracks the record id and (maybe?) which fields dont't match
    """

    # keys: record ID is actually a unique ID for a record (which links to image)
    conflict_id = models.PositiveBigIntegerField(primary_key=True)
    record_id = models.ForeignKey(Record, on_delete=models.CASCADE) 
    conflict_fields = models.TextField()

    def __str__(self):
        return f'Conflict {self.conflict_id} on Record {self.record_id}'


class FormField(models.Model):
    """
    Class to track form x field metadata, i.e. which fields are in which forms

    Users never interact with this model directly, but the app uses it to
    look up which fields to serve the user when they are entering data
    """

    year = models.PositiveIntegerField()
    image_type = models.CharField(max_length=8, null=True, choices = IMAGE_TYPE_CHOICES)
    form_type = models.CharField(max_length=200, choices=FORM_CHOICES)     

    field_name = models.CharField(max_length=50)


class Entry(models.Model):
    """
    Class to track entry metadata (each time user clicks submit)
    """

    record_id = models.ForeignKey(Record, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=8)
    submit_time = models.DateTimeField()
    app_version = models.DecimalField(max_digits=4, decimal_places=1)