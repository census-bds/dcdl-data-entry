"""
MODELS FOR DCDL DATA ENTRY
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
        - last_modified: date at which any reel attribute was last changed (auto-update)
        - create_date: date on which reel instance was created here (auto-update)
        - reel_name: name of reel directory, e.g. 1980_Texas_3951
        - reel_chunk_name: name of 500ish image chunk in a reel, e.g. 1980_Texas_3951_1
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
    reel_chunk_name = models.CharField(max_length = 255, null = False)
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
                fields = ['reel_path', 'reel_chunk_name', 'year'],
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

    Constraints: None

    Methods: 
    - set_image_path(self, path_IN): helper method for loading, sets the file
      path fields

    Attributes:
        Foreign keys:
        - img_reel: links to the Reel model
        Upon load:
        - img_path: full path to the .jpg file on server, including image 
          filename
        - img_file_name: the original image filename including extension
        - img_folder_path: full path to the .jpg file, excluding image filename
        - img_position: integer index tracking image order within reel
        - smaller_image_file_name: filename of compressed image, which is 
          served by app (depending on when shrinking was done, may be the same 
          as img_file_name)
        - create_date: timestamp from instance creation, at image loading
        - year: the year of the reel to which this image belongs

    __str__() prints out an id, the filepath, and related information from the 
    associated reel.
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

        # render string
        string_OUT = " - ".join( string_list )

        return string_OUT

    #-- END overridden built-in method __str__() --#


    def set_image_path( self, path_IN ):
        '''
        Helper method for loading. Sets the img_path, img_file_name, and
        img_folder_path attributes.
        '''

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

    Assignments of an ImageFile to a keyer are stored here. Keyers work through
        their assigned images in reel, then position order. Prior to keying, we
        know the filename/path, but not image type (sheet, breaker, other, etc)

    Constraints:
    - unique on image file *and* jbid 

    Methods:
    - has_related_objects(): helper method that checks for child Breakers or 
    Sheets, to prevent data loss resulting from a keyer changing the Image 
    type. 

    Attributes:
        Foreign keys:
        - image_file
        Upon creation (happens when a keyer is assigned to a reel):
        - keyer jbid
        - year of image
        - create_date
        Entered data:
        - image_type: identifies what type of form is captured in the image
        - is_complete: boolean denoting whether data entry has been completed 
        - timestamp: should be a last_modified timestamp
        - problem: boolean indicating when keyer reported issue with image
        - prob_description: text keyer entered describing the problem
        - flagged_view: which page keyer used when they reported a problem

    __str__() prints out the Image ID, year, and type, as well as the 
    associated ImageFile ID and path.
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
        '''
        Checks for breakers and sheets related to an image. Used to ensure
        foreign keys are preserved during image keying. 
        '''

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
    Class defining information captured for a breaker sheet

    Constraints:
    - unique on Image and jbid

    Attributes:
        Foreign keys:
        - image instance
        Upon data entry for a given breaker:
        - keyer jbid
        - timestamp at creation
        - problem
        - year: derived from reel
        - state: derived from reel
        - create date
        - last modified
        Data fields:
        - county
        - enumeration district
        - mcd
        - tract
        - place
        - smsa

    __str__() prints out a string with related Image instance and keyer jbid
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
        max_length=255
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

    Constraints:
    - unique on image and jbid

    Attributes: 
        Attributes:
        - keyer jbid
        Foreign keys
        - image: foreign key to EntryApp.Image model
        - sheet object: foreign key to EntryApp.Sheet model
        Form data:
        - sample_key: contains sample key radio data
        - address_one: contains text from top long address box (1960 only)
        - address_two: contains text from small bottom address box (1960 only)
        - house_number_one : house number field for top entry (1960 only)
        - house_number_two : house number field for second entry (1960 only)
        - house_number_three : house number field for third entry (1960 only)
        - house_number_four : house number field for fourth entry (1960 only)
        - apt_number_one: apartment number for top entry (1960 only)
        - apt_number_two: apartment number for second entry (1960 only)
        - apt_number_three: apartment number for third entry (1960 only)
        - apt_number_four: apartment number for fourth entry (1960 only)
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

    # hard to read checkbox for 1960
    hard_to_read = models.BooleanField(
        verbose_name = 'Check if you found this image hard to key.', 
        default=False
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
    
    def __str__(self):
        return '{image}: sheet'.format(image = self.img) 


class LongForm1990(models.Model):
    '''
    Class defining the 1990 long form page containing industry and employer

    Constraints:
    - unique on image (foreign key) and jbid

    Attributes:
    - keyer jbid
    - timestamps
    Foreign keys:
    - image object (foreign key)
    Form data:
    - serial_no: household ID
    - person #: the person in household to which this data belongs
    - employer: employer write-in from form
    - industry: industry write-in from form
    - industry_categrory: industry bubble from form
    - occupation: occupation write-in from form
    - occupation_detail: job activity write-in from form
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
        return f"LongForm1990 from {self.jbid}"


class OtherImage(models.Model):
    '''
    Class defining an image that cannot be categorized. Often these are
    cover sheets or problematic scans.

    Constraints:
    - unique on image foreign key and jbid

    Attributes: 
    - image object foreign key
    - jbid of keyer entering data
    - year of image 
    - description: this contains any notes a keyer enters from a free text box
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
    Class defining a single record (one person on a page)

    A sheet image contains 0+ records.

    Constraints: none

    Attributes:
    - jbid of keyer entering data
    - create_date: timestamp when record was generated (automatic)
    - last_modified: timestamp when record was last edited (automatic)
    - timestamp: not actually used
    
    Foreign keys:
    - Sheet: from which the record was entered

    Form_data 
    - line_no: for horizontal forms (1960, 1970), the line number on which this
        person's information appeared
    - col_no: for vertical forms (1980, 1990), the column number in which this
        person's information appears
    
    - first_name: first name of person, if present
    - middle init: middle initial of person, if present
    - last_name: last name of person, if present
    - suffix: person name suffix, e.g. Jr or Sr or II, if present
    - age: numeric age, if present
    - sex: radio button of sex
    - printed_serial_no: printed/written serial no of household. ONLY POPULATED
        FOR THE FIRST LISTED PERSON IN A HOUSEHOLD FOR SPEED OF ENTRY
    - serial_no: written serial number. ONLY POPULATED FOR THE FIRST LISTED 
        PERSON FOR SPEED OF ENTRY
    - block: written block number
    - sample_key_gq: sample key for this household
    - total_persons: total number of persons in household. ONLY POPULATED FOR
        THE FIRST LISTED PERSON IN A HOUSEHOLD FOR SPEED OF ENTRY
    - page_no: page number, when available (1960 only?)
    - relp_writein: character field for write in for relationship to 
        householder
    - race_writein: character field for write in for race
    - tribe_writein: character field for write in for tribe
    - block_1-block_3: 3 radios for the block number bubbles
    - serial_no_1-serial_no_11: 11 radios for the serial number bubbles
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
    total_persons = models.CharField(
        max_length = 255,
        null = True,
        blank = True 
    )

    # 1960 only
    page_no = models.CharField(
        verbose_name = "Page number",
        max_length = 255,
        null = True,
        blank = True
    )

    # write ins
    relp_writein = models.CharField(
        verbose_name = "Relationship to householder (if written)",
        max_length = 255,
        null = True,
        blank = True
    )
    race_writein = models.CharField(
        verbose_name = "Other race (if written)",
        max_length = 255,
        null = True,
        blank = True
    )
    tribe_writein = models.CharField(
        verbose_name = "Indian (Amer.) (if written)",
        max_length = 255,
        null = True,
        blank = True
    )

    # bubble fields
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

    The essential fields used in production views are:
    - jbid
    - img: aka image foreign key
    - breaker: breaker foreign key
    - sheet: sheet foreign key
    - reel: reel foreign key
    - batch_position: boolean to help with edge cases in the "batches" of
        images keyers can have within a reel
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
