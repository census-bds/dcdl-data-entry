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



def load_reel(reel_path, year):
    '''
    Wrapper method to load a reel into the DB
    Used for csv bulk load

    Takes:
    - list of string reel directory filepaths 
    - integer year to which the images belong
    Returns:
    - None
    '''

    _, path_head = os.path.split(reel_path)
    
    # add to Reel model 
    this_reel, _ = Reel.objects.get_or_create(
        reel_path = reel_path,    
        year = year,
        reel_name = path_head
    )

    # call load_imagefiles
    load_imagefiles(reel_path, year)

    return


#-- END function load_reel() --#


def create_1990_dummy_breakers(keyer_jbids=[]):
    '''
    Create default breaker for 1990 for each user, plus associated dummy image

    1990 doesn't have breakers but they are required in the models. This
    function creates a dummy image and breaker for each user for 1990 to avoid
    raising an error when a user enters a sheet without having entered a breaker.
    Dummy images can be identified using the filename pattern
    "dummy_1990_breaker_JBID."

    If you're loading the DB for the first time, there's no need to specify 
    jbids because the default is to use all keyers. If instead you have added a
    new user, you wil need to add a dummy breaker for that user, so you will
    need to specify their jbid.

    Takes:
    - optional list of string jbids (if adding users)
    Returns: none
    '''

    # declare variables
    dummy_breaker_reel_name = None
    dummy_breaker_file_name = None
    image_file_qs = None
    image_file_count = None
    image_file = None

    if not keyer_jbids:
        keyer_jbids = [k.jbid for k in Keyer.objects.all()]

    # get or create reel for dummy breaker
    dummy_reel, _ = Reel.objects.get_or_create(
        reel_name = 'dummy_breaker_reel',
        reel_path = '/data/data/images/dev_images/1990breaker/',
        year = 1990,
        image_count = 1
    )
    
    # get ImageFile for breaker.
    dummy_breaker_file_name = "dummy_1990_breaker"
    image_file_qs = ImageFile.objects.filter( img_path = dummy_breaker_file_name )
    image_file_count = image_file_qs.count()
    if ( image_file_count == 0 ):

        # make new.
        image_file_instance = ImageFile()
        image_file_instance.set_image_path( dummy_breaker_file_name )
        image_file_instance.img_reel = dummy_reel
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

    for k in keyer_jbids:

        img = Image.objects.create(
            image_file = image_file_instance,
            jbid=k,
            is_complete=True,
            year=1990,
            image_type="breaker"
        )

        breaker = Breaker.objects.create(
            year=1990,
            jbid=k,
            img=img
        )

#-- END function create_1990_dummy_breakers() --#


def load_imagefiles(reel_path, year):
    '''
    Loads images from a given reel into ImageFile model.
    Expects .jpg images.

    Takes:
    - reel filepath
    - year
    Returns: None
    '''

    # declare variables
    file_counter = None
    full_file_path = None
    image_file_qs = None
    image_file_count = None
    image_file = None


    files = glob.glob(reel_path + "*.jpg")
    print(f'load_imagefiles() files on {reel_path} are: {files}')

    # get reel associated with this filepath and year
    parent_reel = Reel.objects.filter(year=year).filter(reel_path=reel_path).get()

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

    # set the number of images in reel to number of files
    parent_reel.image_count = file_counter
    parent_reel.save()

    return

#-- END function load_imagefiles() --#


def delete_model_data(reset_keyers = True):
    '''
    Deletes all rows in specified tables
    Optionally resets all keyer reel counts to 0
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

    if reset_keyers:
        for k in Keyer.objects.all():
            k.reel_count = 0
            k.save()


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


def load_form_fields(field_tbl_path=settings.FORM_FIELDS_CSV, reload=True):
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


def load_reels_from_csv(reel_csv_path):
    '''
    Load images from a bunch of reels as specified in a csv

    Takes: string path to reel_csv
    Returns: None
    '''

    with open(reel_csv_path) as f:
        csvreader = csv.reader(f)
        next(csvreader) # skip header row
    
        for row in csvreader:
            logger.info(row)

            load_reel(reel_path = row[0], year = row[1])


def refresh_db():
    '''
    INTENDED FOR DEV ONLY
    Convenience function to wipe existing rows and reload Images
    '''
    delete_model_data()
    load_form_fields(settings.FORM_FIELDS_CSV)
    load_reels_from_csv('dev_reel_load_spec.csv')
    create_1990_dummy_breakers()

    # for k in Keyer.objects.all():
    #     assign_reel(k, {})


def bulk_load_db():
    '''
    Function to load form fields, images, and dummy 1990 breakers
    FOR PRODUCTION
    '''
    load_form_fields(settings.FORM_FIELDS_CSV)
    load_reels_from_csv('dev_reel_load_spec.csv')
    create_1990_dummy_breakers([])
