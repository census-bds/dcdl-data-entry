"""
MODELS FOR DCDL DATA ENTRY

TO DO:
-Validation (or do in forms?)
"""

import logging
import os

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

import EntryApp.choices as choices

#==============================================================================#
# LOGGER
#==============================================================================#

logger = logging.getLogger(__name__)

class CustomAdapter(logging.LoggerAdapter):
    ''' Custom class for adding keyer id to log output '''

    def process(self, msg, kwargs):
        return '%s %s' % (self.extra['user'], msg), kwargs

adapter = CustomAdapter(logger, {'user': '_'})

#=====================================================#
# MODELS FOR TRACKING DATA ENTRY
#=====================================================#


class Keyer(models.Model):
    '''
    Model to track keyer work and determine reel assignment

    Attributes:
    - user: foreign key to Django auth_user model
    - jbid: string of keyer James Bond ID
    - reel_count: count of complete reels assigned

    __str__ shows the keyer's JBID
    '''

    user = models.ForeignKey(User, on_delete = models.CASCADE)
    jbid = models.CharField(max_length=255, default='jbid000')
    reel_count = models.IntegerField(default = 0)

    def __str__(self):
        string_OUT = f'{self.jbid}'
        return string_OUT


class Reel(models.Model):
    '''
    Model to track assignment of reels to users and reel completion. 

    Constraints:
    - unique on reel_path and year
    - specified state must be in valid list of postal abbreviations

    Methods:
    - get_keyer_one(): prints jbid or '' for first assigned keyer
    - get_keyer_two(): prints jbid or '' for second assigned keyer
    
    Attributes:
        Upon load:
        - image_count: number of images (aka files) in the reel
        - is_complete_keyer_one: boolean == True when keyer one finishes entry
        - is_complete_keyer_one: boolean == True when keyer two finishes entry
        - last modified: date at which any reel attribute was last changed (auto-update)
        - load date: date on which reel instance was created here (auto-update)
        - reel_name: name of reel directory, e.g. 1980_Texas_3951
        - reel_path: full file path to reel images on disk
        - state: state covered for 1960-1980
        - year: year of reel
        At reel assignment:
        - keyer_count: number of keyers currently assigned to reel
        - keyer_one: foreign key to EntryApp.Keyer, first assigned keyer
        - keyer_two: foreign key to EntryApp.Keyer, second assigned keyer
        Extra metadata:
        - reel_index: space for a numeric index
        - reel_label: space for some annotation

    __str__ prints a string like "Reel <reel_name> <year>"
    '''

    # metadata that comes in from load
    reel_name = models.CharField(max_length = 255, null = False)
    year = models.IntegerField(blank = True, null = False)
    reel_path = models.CharField(max_length = 255, null = False)
    state = models.CharField(max_length = 255, null = False, default = "--")    
    image_count = models.PositiveIntegerField(null = True)
    keyer_count = models.PositiveIntegerField(null = False, default = 0)

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # set these when the reel is assigned to first and second keyer
    keyer_one = models.ForeignKey(
        Keyer,
        on_delete = models.CASCADE,
        related_name = 'keyer_one',
        null = True
    )  
    is_complete_keyer_one = models.BooleanField(null=False, default=False)
 
    keyer_two = models.ForeignKey(
        Keyer,
        on_delete = models.CASCADE,
        related_name = 'keyer_two',
        null = True
    )  
    is_complete_keyer_two = models.BooleanField(null=False, default=False)

    # optional extra metadata
    reel_index = models.IntegerField(blank = True, null = True )
    reel_label = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['reel_path', 'year'],
                name='unique_reel'
            ),
            models.CheckConstraint(
                check = models.Q(state__in=choices.STATE_LIST),
                name = 'valid state postal abbreviation'
            )
        ]


    def __str__(self):
        
        string_list = [
            'Reel',
            self.reel_name,
            str(self.year)
        ]

        return ' '.join(string_list)

    # method to print jbid for first keyer
    def get_keyer_one(self):

        keyer_one_jbid = self.keyer_one.jbid

        if keyer_one_jbid:
            return keyer_one_jbid
        else:
            return ''

    # method to print jbid for second keyer
    def get_keyer_two(self):

        keyer_two_jbid = self.keyer_two.jbid

        if keyer_two_jbid:
            return keyer_two_jbid
        else:
            return ''


class ImageFile(models.Model):

    """
    Base class for all raw image files. Captures path, information on physical
        location of image that was scanned (reel and position within reel?).

    Once coding is completed, then harmonized "truth" can be stored referring to
        this record separate from coding, so coding is preserved. Could have
        separate copy of tables, or just make a "harmonized_data" user and their
        data is considered the baseline.

    To assign an image for coding, then, you create an Image record for each
        user who should code a particular ImageFile.

    Need also to decide which things are here, and which are in Images.
    """

    # we will bulk load DB with all images to enter
    img_path = models.CharField( max_length = 255, unique = True )
    img_file_name = models.CharField( max_length = 255 )
    img_folder_path = models.CharField( max_length = 255, blank = True, null = True )
    img_reel = models.ForeignKey( Reel, on_delete=models.CASCADE, blank = True, null = False)
    img_position = models.IntegerField()

    # name of compressed version
    smaller_image_file_name = models.CharField( max_length = 255, default = "")

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    # could keep these... these values will be populated as entry proceeds
    year = models.IntegerField( blank = True, null = True )
    image_type = models.CharField(
        max_length=8,
        blank = True,
        null = True,
        choices = choices.IMAGE_TYPE_CHOICES
    )

    # metadata
    is_complete = models.BooleanField(null=True) # need a validation constraint here
    timestamp = models.DateTimeField( blank = True, null = True )
    problem = models.BooleanField( default = False )
    prob_description = models.TextField(
        verbose_name = "Please describe the problem.",
        blank = True,
        null = True
    )
    flagged_view = models.CharField( max_length = 255, blank = True, null = True )

    #class Meta:
    #    constraints = [
    #        models.UniqueConstraint(
    #            fields = ['img_path', 'jbid',],
    #            name='unique_img_entry'
    #        )
    #    ]

    def __str__(self):

        # return reference
        string_OUT = None

        # declare variables
        string_list = None

        # init
        string_list = []
        string_OUT = ""

        # id
        if ( self.id is not None ):

            string_list.append( "{}".format( self.id ) )

        #-- END check if id. --#

        # path
        string_list.append( "path: {}".format( self.img_path ) )

        # reel
        string_list.append( "reel: {reel_label}".format( reel_label = self.img_reel ) )

        # position
        string_list.append( "position: {}".format( self.img_position ) )

        # problem?
        string_list.append( "problem?: {}".format( self.problem ) )

        # render string
        string_OUT = " - ".join( string_list )

        return string_OUT

    #-- END overridden built-in method __str__() --#


    def set_image_path( self, path_IN ):

        # return reference
        value_OUT = None

        # declare variables
        path_head = None
        path_tail = None

        if ( ( path_IN is not None ) and ( path_IN != "" ) ):

            # get folder path and file name from path.
            path_head, path_tail = os.path.split( path_IN )
            print( "- file_path: {head} / {tail}".format( head = path_head, tail = path_tail ) )

            # store path, file name (tail) and folder path (head)
            self.img_path = path_IN
            self.img_file_name = path_tail
            self.img_folder_path = path_head

        else:

            # set all three related fields to None.
            self.img_path = None
            self.img_file_name = None
            self.img_folder_path = None

        #-- END check to see if path passed in. --#

        value_OUT = path_IN

        return value_OUT

    #-- END method set_image_path() --#


#-- END model class ImageFile --#

#=====================================================#
# MODELS FOR DATA ENTRY
#=====================================================#

class Image(models.Model):

    """
    Base class for all image coding.

    Assignments of an ImageFile to a coder are stored here. Coders work through
        their assigned images in reel, then position order. If you need it,
        could use this model to store information on different order.

    Here, we know the filename/path, but need to enter what kind
    of image it is (sheet vs. breaker)
    """

    # we will bulk load DB with all images to enter
    image_file = models.ForeignKey(
        ImageFile,
        on_delete = models.CASCADE,
        blank = True,
        null = True
    )

    # this should get populated when instances are created
    jbid = models.CharField(
        max_length=20,
        default='jbid000'
    )
    year = models.IntegerField( blank = True, null = False )

    # these values will be populated as entry proceeds
    image_type = models.CharField(
        max_length=255,
        null=True,
        choices = choices.IMAGE_TYPE_CHOICES,
        default = None
    )

    # metadata
    is_complete = models.BooleanField( blank = True, null = True ) 
    timestamp = models.DateTimeField( blank = True, null = True )

    # fields that come in from reporting a problem 
    problem = models.BooleanField( default = False )
    prob_description = models.TextField(
        verbose_name="Please describe the problem.",
        blank = True,
        null=True
    )
    flagged_view = models.CharField(max_length=255, blank = True, null = True )

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['image_file', 'jbid',],
                name='unique_img_entry'
            )
        ]

    def __str__(self):

                # return reference
        string_OUT = None

        # declare variables
        string_list = None

        # init
        string_list = []
        string_OUT = ""

        # id
        if ( self.id is not None ):

            string_list.append( "{}".format( self.id ) )

        #-- END check if id. --#

        # got a related image file?
        if ( self.image_file is not None ):

            # ID
            string_list.append( "file ID: {}".format( self.image_file.id ) )

            # path
            string_list.append( "file path: {}".format( self.image_file.img_path ) )

        #-- END information on related image file. --#

        # year
        string_list.append( "year: {}".format( self.year ) )

        # image_type
        string_list.append( "type: {}".format( self.image_type ) )

        # render string
        string_OUT = " - ".join( string_list )

        return string_OUT

    #-- END overridden built-in __str__() method --#

    def has_related_objects( self ):

        # return reference
        has_related_OUT = False

        # declare variables
        me = "Image.has_related_objects"
        status_message = None
        my_type = None
        my_breaker_qs = None
        my_breaker_count = None
        my_sheet_qs = None
        my_sheet_count = None

        # get type
        my_type = self.image_type

        # look for all children, regardless of type - log a message if child is
        #     counter to type.

        # breakers
        my_breaker_qs = self.breaker_set.all()
        my_breaker_count = my_breaker_qs.count()
        if ( my_breaker_count > 0 ):
            has_related_OUT = True
            if ( my_type != choices.IMAGE_TYPE_BREAKER ):
                status_message = "WARNING - there are associated breakers for image of type {image_type} ( image: {me} ).".format(
                    image_type = my_type,
                    me = self
                )
                adapter.warning( status_message, {'user': 'models'} )
            #-- END check if type matches what found records. --#
        #-- END check if related breakers --#

        # sheets
        my_sheet_qs = self.sheet_set.all()
        my_sheet_count = my_sheet_qs.count()
        if ( my_sheet_count > 0 ):
            has_related_OUT = True
            if ( my_type != choices.IMAGE_TYPE_SHEET ):
                status_message = "WARNING - there are associated sheets for image of type {image_type} ( image: {me} ).".format(
                    image_type = my_type,
                    me = self
                )
                adapter.warning( status_message, {'user': 'models'} )
            #-- END check if type matches what found records. --#
        #-- END check if related breakers --#

        return has_related_OUT

    #-- END method has_related_objects() --#

#-- END model Image --#


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
    jbid = models.CharField(max_length=20, default='jbid000')
    timestamp =  models.DateTimeField(null=True)
    problem = models.BooleanField(default=False)

    # TO DO: validation for states
    year = models.IntegerField(
        null=True,
        choices=choices.YEAR_CHOICES[:3]
    )
    # ^ remove 1990 as option because that census did not include breakers
    state = models.CharField(
        max_length=25,
        null=True,
        blank=False,
        choices=choices.STATE_CHOICES,
        default=None
    )
    county = models.CharField(
        max_length=255,
        null=True
    )
    enumeration_district = models.CharField(
        verbose_name = "Enumeration District (ED)",
        max_length=255,
        null=True
    )
    mcd = models.CharField(
        verbose_name = "MCD",
        max_length=255,
        null=True
    )
    tract = models.CharField(
        max_length=255,
        null=True
    )
    place = models.CharField(
        max_length=255,
        null=True
    )
    smsa = models.CharField(
        verbose_name = "SMSA",
        max_length=255,
        null=True
    )

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

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
    jbid = models.CharField(max_length=20, default='jbid000')

    # auto-filled, not required
    timestamp =  models.DateTimeField(null=True)
    year = models.IntegerField(
        null=True,
        choices=choices.YEAR_CHOICES
    )
    problem = models.BooleanField(default=False)

    # for entry
    num_records = models.CharField(
        verbose_name = 'Number of records',
        max_length = 255,
        null = True,
        blank = True
    )

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    def __str__(self):
        return f'{self.img}: sheet' # FIX THIS


class Household1960(models.Model):
    '''
    Class defining the entry for household level info for address for 1960

    Constraints:
    - unique on keyer jbid and sheet ID 

    Attributes:
        - keyer jbid
        Foreign keys
        - image: foreign key to EntryApp.Image model
        - sheet object: foreign key to EntryApp.Sheet model
        Form data:
        - sample_key: contains sample key radio data
        - address_one: contains text from top long address box
        - address_two: contains text from small bottom address box
        - house_number_one : house number field for top entry
        - house_number_two : house number field for second entry
        - house_number_three : house number field for third entry
        - house_number_four : house number field for fourth entry
        - apt_number_one: apartment number for top entry
        - apt_number_two: apartment number for second entry
        - apt_number_three: apartment number for third entry
        - apt_number_four: apartment number for fourth entry
        Additional data collected
        - num_records_one: number of names listed in first household 
        - num_records_two: number of names listed in second household 
        - num_records_three: number of names listed in third household 
        - num_records_four: number of names listed in fourth household 
    '''

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['jbid', 'sheet_id'],
                 name = 'unique_household1960_entry'
            )
        ]
    
    # foreign keys
    image = models.ForeignKey(Image, on_delete = models.CASCADE)
    sheet = models.ForeignKey(Sheet, on_delete = models.CASCADE)

    # keyer id
    jbid = models.CharField(
        max_length = 255,
        default = 'jbid000'
    ) 

    num_records_one = models.PositiveIntegerField(
        verbose_name = 'Number of persons in household 1',
        null=False
    )
    num_records_two = models.PositiveIntegerField(
        verbose_name = 'Number of persons in household 2',
        null=False
    )
    num_records_three = models.PositiveIntegerField(
        verbose_name = 'Number of persons in household 3',
        null=False
    )
    num_records_four = models.PositiveIntegerField(
        verbose_name = 'Number of persons in household 4',
        null=False
    )

    # addresses
    address_one = models.CharField(
        verbose_name = 'First listed street address',
        max_length = 256,
        null=True,
        blank=True,
    )
    address_two = models.CharField(
        verbose_name = 'Second listed street address',
        max_length = 256,
        null=True,
        blank=True,
    )

    # sample keys
    sample_key_one = models.CharField(
        verbose_name = "First sample key",
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.SAMPLE_GQ_CHOICES,
    )
    sample_key_two = models.CharField(
        verbose_name = "Second sample key",
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.SAMPLE_GQ_CHOICES,
    )
    sample_key_three = models.CharField(
        verbose_name = "Third sample key",
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.SAMPLE_GQ_CHOICES,
    )
    sample_key_four = models.CharField(
        verbose_name = "Fourth sample key",
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.SAMPLE_GQ_CHOICES,
    )


    # house numbers
    house_number_one = models.CharField(
        verbose_name = 'First house number',
        max_length = 256,
        null=True,
        blank=True,
    )
    house_number_two = models.CharField(
        verbose_name = 'Second house number',
        max_length = 256,
        null=True,
        blank=True,
    )
    house_number_three = models.CharField(
        verbose_name = 'Third house number',
        max_length = 256,
        null=True,
        blank=True,
    )
    house_number_four = models.CharField(
        verbose_name = 'Fourth house number',
        max_length = 256,
        null=True,
        blank=True,
    )

    # apartment numbers
    apt_number_one = models.CharField(
        verbose_name = 'First apartment number',
        max_length = 256,
        null=True,
        blank=True,
    )
    apt_number_two = models.CharField(
        verbose_name = 'Second apartment number',
        max_length = 256,
        null=True,
        blank=True,
    )
    apt_number_three = models.CharField(
        verbose_name = 'Third apartment number',
        max_length = 256,
        null=True,
        blank=True,
    )
    apt_number_four = models.CharField(
        verbose_name = 'Fourth apartment number',
        max_length = 256,
        null=True,
        blank=True,
    )
    


class LongForm1990(models.Model):
    '''
    Class defining the 1990 long form page containing industry and employer

    Attributes:
    - image object (foreign key)
    - household ID
    - person #
    - industry 
    - employer
    - jbid
    - timestamp
    '''

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['img', 'jbid'],
                name="unique_1990LF_entry"
            )
        ]
    

    img = models.ForeignKey(Image, on_delete = models.CASCADE)
    jbid = models.CharField(max_length=20, default="jbid000")
    
    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )
    
    serial_no = models.CharField(
        verbose_name = "Household serial number",
        max_length = 255,
        null = True,
        blank = True 
    )
    person_no = models.CharField(
        verbose_name="Person number",
        max_length = 255,
        null = True,
        blank = True
    )
    employer = models.CharField(
        verbose_name="28a. For whom did ... work?",
        max_length=255,
        null = True,
        blank = True
    )
    industry = models.CharField(
        verbose_name = "28b. What kind of business or industry was this?",
        max_length = 255,
        null = True,
        blank = True
    )
    industry_category = models.CharField(
        verbose_name=" 28c. Is this business mainly - Fill ONE circle",
        choices = choices.INDUSTRY_CHOICES,
        max_length = 255,
        default = None,
        null = True,
        blank = True
    )
    occupation = models.CharField(
        verbose_name = "29a. What kind of work was ... doing?",
        max_length = 255,
        null = True,
        blank = True
    )
    occupation_detail = models.CharField(
        verbose_name = "29b. What were ...'s most important activities or duties?",
        max_length = 255,
        null = True,
        blank = True
    )

    def __str__(self):
        return f"LongForm1990 from {self.jbid}: serial_no {self.serial_no} person_no {self.person_no}"


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
    jbid = models.CharField(
        max_length = 255,
        default = 'jbid000'
    )
    year = models.IntegerField(choices = choices.YEAR_CHOICES)
    description = models.TextField(
        max_length = 500,
        verbose_name=''
    )

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    def __str__(self):
        return f'{self.img}: OtherImage'


class Record(models.Model):
    """
    Class defining a single record (one person)

    A sheet image contains 1+ records
    """

    # required to uniquely identify the record
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    jbid = models.CharField(
        max_length = 255,
        default = 'jbid000'
    ) 

    # need one or the other of these
    line_no = models.CharField(
        verbose_name = 'Line number',
        null = True,
        blank = True,
        max_length = 255
    )
    col_no = models.CharField(
        verbose_name = 'Column number',
        null = True,
        blank = True,
        max_length = 255
    )


    # fields common among all year-forms
    first_name = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    middle_init = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    last_name = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    suffix = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    age = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    sex = models.CharField(
            choices = choices.SEX_CHOICES,
            max_length = 255,
            blank = False,
            default = None,
            null = True
        )

    # fields that appear in some year-forms but not all
    page_no = models.CharField(
        verbose_name = "Page number",
        max_length = 255,
        null = True,
        blank = True
    )
    person_no = models.CharField(
            verbose_name = "Person number",
            max_length = 255,
            null = True,
            blank = True
        )
    serial_no = models.CharField(
        verbose_name = "Serial number",
        max_length = 255,
        null = True,
        blank = True
    )
    printed_serial_no = models.CharField(
        verbose_name = "Printed serial number (if present)",
        max_length = 255,
        null = True,
        blank = True
    )
    block = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    sample_key_gq = models.CharField(
        verbose_name = "Sample key",
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.SAMPLE_GQ_CHOICES,
    )
    street_name = models.CharField(
        max_length = 255,
        null = True,
        blank = True
    )
    house_no = models.CharField(
        verbose_name = "House number",
        max_length = 255,
        null = True,
        blank = True
    )
    apt_no = models.CharField(
            verbose_name = "Apartment number",
            max_length = 255,
            null = True,
            blank = True
    )

    # relp options vary by year
    relp_1960 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RELP_CHOICES_1960,
        verbose_name = "Relationship to household head"
    )
    relp_1970 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RELP_CHOICES_1970,
        verbose_name = "Relationship to household head"
    )
    relp_1980 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RELP_CHOICES_1980,
        verbose_name = "Relationship to household head"
    )
    relp_1990 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RELP_CHOICES_1990,
        verbose_name = "Relationship to household head"
    )
    race_1960 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RACE_CHOICES_1960,
        verbose_name = "Race"
    )
    race_1970 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RACE_CHOICES_1970,
        verbose_name = "Race"
    )
    race_1980 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RACE_CHOICES_1980,
        verbose_name = "Race"
    )
    race_1990 = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.RACE_CHOICES_1990,
        verbose_name = "Race"
    )
    exact_birth_year = models.CharField(
        verbose_name = 'Year of birth',
        max_length = 255,
        null = True,
        blank = True
    )
    exact_birth_month = models.CharField(
        verbose_name = 'Month of birth',
        max_length = 255,
        null = True,
        blank = True
    )
    birth_year = models.CharField(
        verbose_name = "Specific year of birth",
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.SINGLE_DIGIT_CHOICES
    )
    birth_quarter = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.BIRTH_QUARTER_CHOICES,
        verbose_name = "Month of birth"
    )
    birth_decade = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.BIRTH_DECADE_CHOICES,
        verbose_name = "Decade of birth"
    )

    marital_status = models.CharField(
        max_length = 255,
        blank = False,
        default = None,
        null = True,
        choices = choices.MARITAL_STATUS_CHOICES
    )

    total_persons = models.CharField(
        max_length = 255,
        null = True,
        blank = True 
    )

    # bubble fields

    age_hundreds = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    age_tens = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    age_ones = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )

    birth_year_thousands = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    birth_year_hundreds = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    birth_year_tens = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    birth_year_ones = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )

    block_1 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    block_2 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    block_3 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )


    serial_no_1 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_2 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_2 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_3 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_4 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_5 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_6 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_7 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_8 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_9 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_10 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    serial_no_11 = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )

    total_persons_hundreds = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    total_persons_tens = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )
    total_persons_ones = models.CharField(
        null = True,
        blank = False,
        max_length = 255,
        verbose_name = "",
        choices = choices.SINGLE_DIGIT_CHOICES,
        default = None
    )

    # entry info
    timestamp =  models.DateTimeField(null=True)
    is_complete = models.BooleanField(default=False)

    # automatic create and update time stamps.
    create_date = models.DateTimeField( auto_now_add = True )
    last_modified = models.DateTimeField( auto_now = True )

    def __str__(self):
        return f'Record {self.line_no} {self.jbid} on {self.sheet}: {self.last_name, self.first_name}'

#=====================================================#
# MODELS FOR METADATA AND BACKEND
#=====================================================#

class CurrentEntry(models.Model):

    '''
    Model to track current image and breaker for each user.

    This is essentialy a table of pointer: one row for each user, 
    with foreign keys to link to data models
    '''

    jbid = models.CharField(max_length=255, default='jbid000')
    keyer = models.ForeignKey(Keyer, on_delete=models.CASCADE)

    img = models.ForeignKey(Image, on_delete=models.CASCADE)
    breaker = models.ForeignKey(Breaker, on_delete=models.SET_NULL, null=True)
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, null=True) 

    # track reel and image file  
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    image_file = models.ForeignKey(ImageFile, on_delete=models.CASCADE)

    # track position in batch for improved user experience
    batch_position = models.BooleanField(
        null = False,
        default = False
    )

    def __str__(self):
        return f'CurrentEntry: {self.jbid} entering {self.img}'

    def print_breaker_img(self):
        return f'CurrentEntry breaker img is {self.breaker_img}'

    def get_current_reel(self):
        current_reel = self.img_image_file_image_reel
        return ''


class FormField(models.Model):
    """
    Class to track form x field metadata, i.e. which fields are in which forms

    Users never interact with this model directly, but the app uses it to
    look up which fields to serve the user when they are entering data
    """

    year = models.FloatField()
    form_type = models.CharField(
            max_length=255,
            choices=choices.FORM_CHOICES
        )     
    field_name = models.CharField(max_length=255)

    def __str__(self):
        return f'FormField {self.year} {self.form_type}: {self.field_name}'
