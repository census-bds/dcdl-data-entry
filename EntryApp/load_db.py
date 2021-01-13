#===============================================================#
# LOAD DATA INTO DATABASE
#===============================================================#

import csv
import glob
import json
import logging
import os
from pathlib import Path

# from django.contrib.auth import User
from django.db import connection

from EntryApp.models import Image, Breaker, Sheet, Record, OtherImage, FormField, CurrentEntry

logger = logging.getLogger('EntryApp.load_db')

FORM_FIELDS_CSV = "Z:/1950-1980 censuses/cecile_dev/FormFields.csv"
IMAGE_DIR = "Z:/1950-1980 censuses/cecile_dev/dcdl/images/"


def load_images(path, users, ext = "*.jpg"):
    '''
    Loads images into the DB, 1 row per image-user

    Takes: 
    - string filepath
    - list of username strings
    - file extension (default .jpg)
    Returns: none
    '''

    files = glob.glob(path + ext)
    print(files)

    for f in files:
        for u in users:

            img = Image(img_path=f.split("\\    ")[-1], \
                    jbid=u, \
                    is_complete=False, \
                    year=None, 
                    image_type=None, \
                    problem=False)
            img.save()
    
    return


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


def load_form_fields(field_tbl_path):
    '''
    Load the formfield table into the DB (1 row at a time)

    Takes:
    - path string to csv file mapping fields to years
    '''

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
    '''
    delete_model_data()
    load_form_fields(FORM_FIELDS_CSV)
    load_images(IMAGE_DIR, ['jbid123', 'jbid456'])

#================================#
# AUTHENTICATION 
#================================#

def create_entry_group():
    '''
    Creates the entry group with relevant permissions
    '''
    pass


def create_users(usernames, pws, emails=[]):
    '''
    Create entry accounts for the data entry users

    Takes:
    - list of string usernames
    - list of string passwords
    - optional list of string emails
    '''

    if emails and len(usernames) != len(emails):
        raise IndexError('List of users is not the same length as list of emails.')

    pass