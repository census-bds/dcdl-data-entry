"""
MODELS FOR DCDL DATA ENTRY

TO DO:
-FilePath field type
-Validation
-Nulls and blanks
-keys
"""


from django.db import models

# Create your models here.
class Image(models.Model):
    """
    Abstract base class for all images
    """
    
    image_id = models.CharField(max_length=200)
    year = models.IntegerField()
    is_complete = models.BooleanField()
    date_complete = models.DateTimeField()

    class Meta:
        abstract = True


class Sheet(Image):
    """
    Class defining a record sheet (subclass of image)
    
    Attributes: image_id, year, form_type, breaker_id,
                is_entered, date_complete, num_to_match
    """

    form_type = models.CharField(max_length=200)
    breaker_id = models.CharField(max_length=200)

    def __str__(self):
        return f'Image {self.image_id}: {self.year} {self.form_type}'


class Breaker(Image):
    """
    Class defining a breaker sheet
    """
    
    # geography fields
    # TO DO: fix types and do validation
    state = models.CharField(max_length=2) # valid list of states
    county = models.CharField(max_length=30)
    enum_dist = models.CharField(max_length=30)
    mcd = models.CharField(max_length=30)
    tract = models.CharField(max_length=30)
    place = models.CharField(max_length=30)
    smsa = models.CharField(max_length=30)
    large_do_ed = models.CharField(max_length=30) #TO DO: ask Katie what this is
    
    def __str__(self):
        return f'Breaker {self.image_id} from {self.year}'


class Record(models.Model):
    """
    Class defining a single record (one person)

    A sheet image contains 1+ records
    """

    # link to the image 
    record_id = models.PositiveSmallIntegerField(primary_key=True) # this is row (or col)
    image_id = models.ForeignKey(Sheet, on_delete=models.CASCADE)

    # fields common among all year-forms
    first_name = models.CharField(max_length=50)
    middle_init = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    sex = models.BooleanField(choices=[(0, 'Male'), (1, 'Female')]) # fix this

    # fields that appear in some year-forms but not all
    race = models.CharField(max_length=50) 
    page_no = models.PositiveIntegerField()
    line_no = models.PositiveIntegerField() # this may be row or col no
    serial_no = models.IntegerField()
    block = models.CharField(max_length=50)
    sample_key_gq = models.CharField(max_length=50)
    relp = models.CharField(max_length=50)
    ind = models.CharField(max_length=50)
    occp = models.CharField(max_length=50)
    birth_year = models.PositiveIntegerField()
    birth_month = models.CharField(max_length=15)
    total_persons = models.PositiveIntegerField()

    # entry info
    user_id = models.CharField(max_length=50)
    entry_time = models.DateTimeField()
    is_illegible = models.BooleanField()


    def __str__(self):
        return f'Record {self.record_id}: {self.last_name, self.first_name}'


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
