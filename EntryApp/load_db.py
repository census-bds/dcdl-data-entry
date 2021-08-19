#===============================================================#
# LOAD IMAGES INTO DATABASE
#===============================================================#

import csv
import glob
import json
import logging
import os
import socket
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import connection

from EntryApp.models import Breaker
from EntryApp.models import CurrentEntry
from EntryApp.models import ImageFile
from EntryApp.models import Image
from EntryApp.models import Keyer
from EntryApp.models import FormField
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Reel
from EntryApp.models import Sheet

logger = logging.getLogger('EntryApp.load_db')


def get_next_keyers():
    '''
    Looks in Keyer model to identify which two keyers to assign to new reel
    Updates Keyer model to increment reel_count and is_next

    Takes: None
    Returns: Keyer queryset
    '''

    keyer_qs = Keyer.objects.filter(is_next = True)

    # check that the length of this queryset is exactly 2
    if len(keyer_qs) != 2:
        print(f'keyer_qs has wrong length: expected 2, got {len(keyer_qs)}')

    # find the keyers after this, set them to next
    next_keyers = Keyer.objects.order_by('reel_count')[:2]

    for k in next_keyers:
        k.is_next = True
        k.save()

    # increment reel count for current keyers, set is_next to False
    for k in keyer_qs:
        k.reel_count += 1
        k.is_next = False
        k.save()

    return keyer_qs 

#--- END get_next_keyers() ---#


def load_images(filepath, year, keyers=[]):
    '''
    Loads images from a given reel into ImageFile and Image models. 
    Expects .jpg images. 

    Required arguments:
    - string filepath to images, e.g. /data/data/images/1960/a_1960_reel/
    - integer year (the decennial year to which images belong)
    Optional arguments:
    - list of keyer username strings (will look up next if none provided)
    - file extension (default .jpg)
    Returns: none
    '''

    # declare variables
    file_counter = None
    full_file_path = None
    image_file_qs = None
    image_file_count = None
    image_file = None

    files = glob.glob(filepath + "*.jpg")
    print(files)

    # if no list of users was provided, look up next in table
    if not keyers:
        keyer_qs = get_next_keyers()
        keyer_jbids = [k.jbid for k in keyer_qs]

    # check that there are exactly two keyers
    if len(keyers) != 2:
        print(keyers)
        raise ValueError

    # get reel associated with this filepath and year
    parent_reel = Reel.objects.filter(year=year).filter(reel_path=filepath).get()

    # loop over files in current path.
    file_counter = 0
    for full_file_path in files:

        file_counter += 1

        # create ImageFile?
        image_file_qs = ImageFile.objects.filter( img_path = full_file_path )
        image_file_count = image_file_qs.count()
        if ( image_file_count == 0 ):


            # make new.
            image_file_instance = ImageFile()
            image_file_instance.set_image_path( full_file_path )
            image_file_instance.img_position = file_counter
            image_file_instance.year = year
            image_file_instance.img_reel = parent_reel
            image_file_instance.save()
            

        elif ( image_file_count == 1 ):

            # load existing
            image_file_instance = image_file_qs.get()

        else:

            # more than 1? Oh dear...
            print( "ERROR - more than one ImageFile for path {image_path} - punting for now.".format( image_path = file_path ) )
            image_file_instance = None

        #-- END check to see if we already have instance for this file path. --#

        #print( "----> ImageFile: {image_file}".format( image_file = image_file_instance ) )

        for k in keyers:

            img = Image.objects.create( 
                    image_file=image_file_instance, \
                    jbid=k, \
                    is_complete=False, \
                    year=year,
                    image_type=None, \
                    problem=False
            )

        #-- END loop over users for a given file --#

    #-- END loop over files in chosen folder --#

    return

#-- END function load_images() --#


def load_reel(reel_path, year, keyers=[]):
    '''
    Wrapper method to load images from a reel
    Used for csv bulk load

    Takes:
    - list of string reel directory filepaths 
    - integer year to which the images belong
    - optional list of keyers to assign 
    Returns:
    - None
    '''

    # if no list of users was provided, look up next in table
    if not keyers:
        keyers = get_next_keyers()
        print(keyers)

    # check that there are exactly two keyers
    if len(keyers) != 2:
        print(keyers)
        raise ValueError

    _, path_head = os.path.split(reel_path)
    
    # add to Reel model 
    this_reel = Reel.objects.get_or_create(
        reel_path = reel_path,    
        year = year,
        reel_name = path_head,
        keyer_one = keyers[0],
        keyer_two = keyers[1]
    )

    # call load_images
    keyer_jbids = [k.jbid for k in keyers]
    load_images(reel_path, year, keyer_jbids)


#-- END function load_reel() --#


def create_1990_dummy_breakers(users):
    '''
    Create default breaker for 1990 for each user, plus associated dummy image

    1990 doesn't have breakers but they are required in the models. This
    function creates a dummy image and breaker for each user for 1990 to avoid
    raising an error when a user enters a sheet without having entered a breaker.
    Dummy images can be identified using the filename pattern
    "dummy_1990_breaker_JBID."

    Takes:
    - list of string usernames
    Returns: none
    '''

    # declare variables
    dummy_breaker_file_name = None
    image_file_qs = None
    image_file_count = None
    image_file = None

    if not users:
        g = Group.objects.get(name='data_entry')
        users = [u.username for u in g.user_set.all()]

    # get ImageFile for breaker.
    dummy_breaker_file_name = "dummy_1990_breaker"
    image_file_qs = ImageFile.objects.filter( img_path = dummy_breaker_file_name )
    image_file_count = image_file_qs.count()
    if ( image_file_count == 0 ):

        # make new.
        image_file_instance = ImageFile()
        image_file_instance.set_image_path( dummy_breaker_file_name )
        image_file_instance.img_reel_label = dummy_breaker_file_name
        image_file_instance.img_reel_index = 0
        image_file_instance.img_position = 1
        image_file_instance.save()

    elif ( image_file_count == 1 ):

        # load existing
        image_file_instance = image_file_qs.get()

    else:

        # more than 1? Oh dear...
        print( "ERROR - more than one ImageFile for path {dummy_breaker_file_name} - punting for now.".format( image_path = file_path ) )
        image_file_instance = None

    #-- END check to see if we already have instance for this file path. --#

    #print( "----> ImageFile: {image_file}".format( image_file = image_file_instance ) )

    for u in users:

        img = Image.objects.create(
            image_file = image_file_instance,
            jbid=u,
            is_complete=True,
            year=1990,
            image_type="breaker"
        )

        breaker = Breaker.objects.create(
            year=1990,
            jbid=u,
            img=img
        )


def delete_model_data():
    '''
    Deletes all rows in specified tables
    '''

    data_models = [
        Breaker, \
        CurrentEntry, \
        FormField, \
        ImageFile, \
        Image, \
        OtherImage, \
        Record, \
        Reel, \
        Sheet,
    ]

    for m in data_models:
        m.objects.all().delete()


def create_image_fixture(path, users, out, ext="*.jpg"):

    '''
    Creates a JSON fixture to load for the image table

    Should be able to do this with:
    python manage.py dumpdata EntryApp
    OR
    python manage.py dumpdata EntryApp.ImageFile EntryApp.Image

    Also, this will break now. Sorry!

    Takes:
    - string filepath to images
    - list of username strings
    - path to store output JSON
    - file extension (default .jpg)
    Returns: none
    '''

    full_path = Path(__file__).parent.parent.joinpath(Path(path))
    files = glob.glob(str(full_path) + os.sep + ext)

    image = []
    i=0

    for f in files:
        for u in users:

            image.append(
                {
                    'model': 'EntryApp.image',
                    'pk': i,
                    'fields': {
                        'img_path': f.split(os.sep)[-1],
                        'jbid': u,
                        'is_complete': False,
                        'year': None,
                        'image_type': None,
                        'timestamp': None
                    }
                })
            i+=1

    out = Path(__file__).parent.parent.joinpath(Path(out))
    with open(str(out), 'w') as json_file:
        json.dump(image, json_file)


def load_form_fields(field_tbl_path, reload=True):
    '''
    Load the formfield table into the DB (1 row at a time)

    Takes:
    - path string to csv file mapping fields to years
    - optional boolean if keeping what's in the FormField model
    '''

    if reload:
        FormField.objects.all().delete()

    with open(field_tbl_path) as f:
        csvreader = csv.reader(f)
        next(csvreader) # skip header row

        for row in csvreader:
            logger.info(row)
            field = FormField(year = row[0], form_type=row[1], field_name=row[2])
            field.save()


def refresh_db():
    '''
    INTENDED FOR DEV ONLY
    Convenience function to wipe existing rows and reload Images
    '''
    delete_model_data()
    load_form_fields(settings.FORM_FIELDS_CSV)
    load_images(settings.IMAGE_DIR, 1960, ['jbid123', 'jbid456'])
    create_1990_dummy_breakers(['jbid123', 'jbid456'])


def bulk_load_db():
    '''
    Function to load form fields, images, and dummy 1990 breakers
    FOR PRODUCTION
    '''
    load_form_fields(settings.FORM_FIELDS_CSV)
    load_images(settings.IMAGE_DIR, [])
    create_1990_dummy_breakers([])
