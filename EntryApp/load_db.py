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
from EntryApp.models import FormField
from EntryApp.models import OtherImage
from EntryApp.models import Record
from EntryApp.models import Sheet


logger = logging.getLogger('EntryApp.load_db')


def load_images(path, year, users=[], ext = "*.jpg", reel_label_IN = None, reel_index_IN = None ):
    '''
    Loads images into the DB, 1 row per entry-user

    Required arguments:
    - string filepath
    - integer year (the decennial year to which images belong)
    Optional arguments:
    - list of username strings (default all in data_entry group)
    - file extension (default .jpg)
    - reel label (text string)
    - reel index (e.g. reel #2)
    Returns: none
    '''

    # declare variables
    file_reel_label = None
    file_reel_index = None
    file_counter = None
    full_file_path = None
    image_file_qs = None
    image_file_count = None
    image_file = None

    files = glob.glob(path + f'/{year}/' + ext)
    print(files)

    # if no list of users was provided, default to all in data_entry group
    if not users:
        g = Group.objects.get(name='data_entry')
        users = [u.username for u in g.user_set.all()]

    # init reel label and index
    file_reel_label = reel_label_IN
    if ( ( file_reel_label is None ) or ( file_reel_label == "" ) ):

        # no reel string passed in, use path.
        file_reel_label = path

    #-- END check to see if we have a reel string passed in --#

    file_reel_index = reel_index_IN
    if ( file_reel_index is None ):

        # no reel string passed in, use path.
        file_reel_index = 0

    #-- END check to see if we have a reel index passed in --#

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
            image_file_instance.img_reel_label = file_reel_label
            image_file_instance.img_reel_index = file_reel_index
            image_file_instance.img_position = file_counter
            image_file_instance.year = year
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

        for u in users:

            img = Image.objects.create( 
                    image_file=image_file_instance, \
                    jbid=u, \
                    is_complete=False, \
                    year=year,
                    image_type=None, \
                    problem=False
            )

        #-- END loop over users for a given file --#

    #-- END loop over files in chosen folder --#

    return

#-- END function load_images() --#


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
    for m in [ImageFile, Image, Breaker, Sheet, Record, CurrentEntry, FormField, OtherImage]:
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
