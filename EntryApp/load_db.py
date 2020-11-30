#===============================================================#
# LOAD DATA INTO DATABASE
#===============================================================#

import csv
import glob
import logging

from EntryApp.models import Image, FormField

logger = logging.getLogger('EntryApp.load_db')


def load_images(path, users, ext = ".png"):
    '''
    Loads images into the DB, 1 row per image-user

    Takes: 
    - string filepath
    - list of username strings
    - file extension (default .png)
    Returns: none
    '''

    files = glob.glob(path + ext)

    for f in files:
        for u in users:

            img = Image(img_path=f, \
                    jbid=u, \
                    is_complete=False, \
                    year=None, 
                    image_type=None, \
                    date_complete=None)
            img.save()
    
    return


def load_form_fields(field_tbl_path):
    '''
    Load the formfield table into the DB

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