#===============================================================#
# LOAD DATA INTO DATABASE
#===============================================================#

import csv
import glob
import json
import logging
import os
import socket
from pathlib import Path

from django.db import connection
from django.contrib.auth.models import Group

from EntryApp.models import Image, Breaker, Sheet, Record, OtherImage, FormField, CurrentEntry

logger = logging.getLogger('EntryApp.load_db')

if socket.gethostname() == 'erd-web008-dev.compute.csp1.census.gov':
    FORM_FIELDS_CSV = os.path.join(Path(__file__).parent.absolute(), 'FormFields.csv')
    IMAGE_DIR = '/data/data/git/images/'
else: 
    FORM_FIELDS_CSV = "Z:/1950-1980 censuses/cecile_dev/FormFields.csv"
    IMAGE_DIR = "Z:/1950-1980 censuses/cecile_dev/dcdl/images/"


def load_images(path, users=[], ext = "*.jpg"):
    '''
    Loads images into the DB, 1 row per entry-user

    Takes: 
    - string filepath
    - list of username strings (default all in data_entry group)
    - file extension (default .jpg)
    Returns: none
    '''

    files = glob.glob(path + ext)
    print(files)

    if not users:
        g = Group.objects.get(name='data_entry')
        users = [u.username for u in g.user_set.all()]

    for f in files:
        for u in users:

            img = Image(img_path=os.path.split(f)[-1], \
                    jbid=u, \
                    is_complete=False, \
                    year=None, 
                    image_type=None, \
                    problem=False)
            img.save()
    
    return


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

    if not users:
        g = Group.objects.get(name='data_entry')
        users = [u.username for u in g.user_set.all()]

    for u in users:

        img = Image.objects.create(
            img_path=f'dummy_1990_breaker_{u}',
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
    for m in [Image, Breaker, Sheet, Record, CurrentEntry, FormField, OtherImage]:
        m.objects.all().delete()


def create_image_fixture(path, users, out, ext="*.jpg"):
    '''
    Creates a JSON fixture to load for the image table

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
    Convenience function to wipe existing rows and reload Images
    INTENDED FOR DEV ONLY
    '''
    delete_model_data()
    load_form_fields(FORM_FIELDS_CSV)
    load_images(IMAGE_DIR, ['jbid123', 'jbid456'])
    create_1990_dummy_breakers(['jbid123', 'jbid456'])


def bulk_load_db():
    '''
    Function to load form fields, images, and dummy 1990 breakers
    FOR PRODUCTION
    '''
    load_form_fields(FORM_FIELDS_CSV)
    load_images(IMAGE_DIR, [])
    create_1990_dummy_breakers([])