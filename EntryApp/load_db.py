
"""
LOAD IMAGES INTO DATABASE

This module contains methods to help load images into the database after they
have been copied and potentially converted to jpg or shrunk. They are intended
for use in the Django shell.
"""

import csv
import glob
import json
import os
import socket
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import connection

from EntryApp.shrink_images import shrink_reel_images_before_db

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

CHUNK_SIZE = 10000 # deprecated because we realized Reels can't be split 


def load_imagefiles(reel_path, year, chunk_name, image_chunk):
    '''
    Loads images from a given reel into ImageFile model.
    Expects .jpg images.

    Takes:
    - reel filepath
    - year
    - name of the chunk of images
    - lsit of image filepaths
    Returns: None
    '''

    # declare variables
    file_counter = None
    full_file_path = None
    image_file_qs = None
    image_file_count = None
    image_file = None

    # sort the files in this chunk
    files = sorted(image_chunk)

    # get reel associated with this filepath and year
    parent_reel = Reel.objects.filter(year=year).filter(reel_chunk_name=chunk_name).get()

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
            image_file_instance.smaller_image_file_name = image_file_instance.img_file_name #TODO: improve this
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


def chunk_images(image_list, num_images, num_chunks):
    '''
    Cut original list of images into reel into list of N chunks.
    Helper method for reel loading.

    Takes:
    - list of images inside the directory
    - number of chunks to split into
    Returns: 
    - list of N chunks, each containing [CHUNK_SIZE, 2*CHUNK_SIZE) images
    '''

    # if we only need one chunk, we don't need to do anything except wrap
    # the existing list in another list
    if num_chunks == 1:
        chunked_final = [image_list]

    # otherwise break image list into chunks
    else:

        N = CHUNK_SIZE

        # first attempt: cut it into chunks of size N, maybe with a leftover
        chunked = [image_list[i:i + N] for i in range(0, len(image_list), N)] 
        
        print(f"N is {N} and len(chunked) is {len(chunked)}")

        # most likely, # of images in reel is not evenly divisible by chunk size
        # => one extra item in chunked above.
        # however, if it IS evenly divisible, we want to skip this step
        if len(chunked) > num_chunks and num_images % N != 0:

            chunked_final = chunked[0:num_chunks-1]

            combined_last_two_lists = chunked[num_chunks-1] + chunked[-1] 
            chunked_final.append(combined_last_two_lists)

        else:
            
            chunked_final = chunked

        # as long as there is more than one chunk, we should know that:
        # 1. the # of images in any chunk should be at least the specified chunk size
        # 2. the # of images in any chunk should not be more than 2X the chunk size
        #       (otherwise we should have split that into two chunks)
        if len(chunked_final) > 1:
            
            for c in chunked_final:

                print(len(c))
                # must be at least minimum size, otherwise wouldn't have been broken up
                assert len(c) >= CHUNK_SIZE
                # should never be more than 2x chunk size images
                assert len(c) < (2 * CHUNK_SIZE)
        
    return chunked_final


def point_current_entry_to_new_reel(jbid, this_reel):
    '''
    Replace the pointers in CurrentEntry so a keyer can start a new reel. Use
    this method to move a keyer manually. You will delete where they are 
    in the queue of existing images.

    Takes:
    - string keyer jbid
    - instance of the reel to move to
    Returns:
    - None
    '''
    current = CurrentEntry.objects.get(jbid=jbid)
    first_imagefile = ImageFile.objects.filter(img_reel = this_reel)[0]
    first_image = Image.objects.get(
        jbid = jbid,
        image_file = first_imagefile
    )

    current.reel = this_reel
    current.image_file = first_imagefile
    current.img = first_image
    current.save()


def load_reel(reel_path, year, state):
    '''
    Wrapper method to load a reel into the DB
    Used for csv bulk load

    Takes:
    - string reel directory filepath, NOT ending in / 
    - integer year to which the images belong
    - string state abbreviation (postal code)
    Returns:
    - None
    '''

    if reel_path[-1] == '/':
        print("ldb.load_reel() error: please remove the trailing slash from filepath")
        raise ValueError

    _, path_head = os.path.split(reel_path)

    print(f'os.path.split is {os.path.split(reel_path)}')
    print(f'path_head is {path_head}')
    
    # how many images are in here?
    image_list = glob.glob(reel_path + "/*_smaller.jpg")
    num_images = len(image_list)
    num_chunks = max(num_images // CHUNK_SIZE, 1)
    print(f"Splitting {reel_path}  with {num_images} images into {num_chunks} chunks...")


    # make chunk names
    chunk_names = [path_head.rstrip("/") + "_" + str(n) for n in range(num_chunks)]

    # break images into chunks
    chunks = chunk_images(image_list, num_images, num_chunks)

    # loop through them
    for name, chunk in zip(chunk_names, chunks):

        print(f"name is {name} and chunk is {chunk}")

        # add to Reel model 
        this_reel, _ = Reel.objects.get_or_create(
            reel_path = reel_path,    
            year = year,
            reel_name = path_head,
            reel_chunk_name = name,
            state = state
        )

        # call load_imagefiles
        load_imagefiles(reel_path, year, name, chunk)


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
        reel_chunk_name = 'dummy_breaker_reel',
        reel_path = '/data/data/images/dev_images/1990breaker/',
        year = 1990,
        state = 'DC',
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

        image = Image.objects.create(
            image_file = image_file_instance,
            jbid=k,
            is_complete=True,
            year=1990,
            image_type="breaker"
        )

        breaker = Breaker.objects.create(
            year=1990,
            jbid=k,
            img=image,
            state=dummy_reel.state,
            enumeration_district='1234',
        )

#-- END function create_1990_dummy_breakers() --#


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
            print(row)
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
            print(row)
            load_reel(reel_path = row[0], year = row[1], state = row[2])


def assign_reel_to_keyer(this_reel, keyer, keyer_position):
    '''
    Assign a keyer the images from a specified reel by loading image
     info into Image model for a keyer. This method populates the Image model.
    Designed to be used from the django shell.

    Required arguments:
    - reel instance
    - keyer instance 
    - integer 1 or 2 denoting keyer position
    Returns: 
    - None
    '''

    # set the keyer
    if keyer_position == 1:
        this_reel.keyer_one = keyer

    elif keyer_position == 2:
        this_reel.keyer_two = keyer

    else:
        print(f'assign_reel_to_keyer() got wrong number for keyer position')
        raise ValueError

    # increment reel keyer count
    this_reel.keyer_count += 1
    this_reel.save()

    # also increment keyer reel count
    keyer.reel_count += 1
    keyer.save()

    # now, get year and associated image files 
    year = this_reel.year
    image_file_qs = ImageFile.objects.filter(img_reel_id = this_reel)

    # loop through and create Image instance w/this keyer 
    for image_file_instance in image_file_qs:

        img = Image.objects.create( 
                image_file=image_file_instance, \
                jbid=keyer.jbid, \
                is_complete=False, \
                year=year,
                image_type=None, \
                problem=False
        )

    #-- END loop over images in the reel --#

    return 

#-- END assign_reel_to_keyer() method --#


def remove_reel_from_keyer(this_reel, this_keyer, keyer_position, delete_img = False):
    '''
    MOSTLY FOR DEV: BE CAREFUL, THIS DELETES DATA
    De-assigns a keyer from a reel and optionally deletes associated Images
    Takes:
    - reel object
    - keyer object
    - integer keyer position (1 or 2)
    - optional boolean: True will delete associated Images, False will preserve them
    '''

    # remove keyer from position and decrement keyer count
    if keyer_position == 1:
        this_reel.keyer_one_id = None
    elif keyer_position == 2:
        this_reel.keyer_two_id = None
    else:
        print("load_db.remove_reel_from_keyer() got unknown keyer position")
    
    this_reel.keyer_count += -1
    this_reel.save()

    # decrement keyer
    this_keyer.reel_count += -1
    this_keyer.save()

    # delete images if specified 
    if delete_img:

        year = this_reel.year
        image_file_qs = ImageFile.objects.filter(img_reel_id = this_reel)

        # loop through and create Image instance w/this keyer 
        for image_file_instance in image_file_qs:            
            image_qs = Image.objects.filter(image_file =  image_file_instance)
            image = image_qs.filter(jbid = this_keyer.jbid).get()
            image.delete()

    return

#-- END remove_reel_from_keyer() method --#


def assign_training_reels_to_all_keyers(reel, slot_to_assign):
    '''
    Assigns all keyers one of the copies of the specified reel. This method
    is a convenience for provisioning the training database and doesn't
    handle several possible cases, including more keyers than training copies
    and some reels already partially assigned. 

    Takes:
    - string base name of reel, e.g. "1980_Texas_123"
    - keying position on the reel (1 or 2)
    Returns:
    - None
    '''

    # get all keyers and all copies of the training reel
    keyers = Keyer.objects.all()
    reel_qs = Reel.objects.filter(reel_name__startswith=reel).order_by("id")

    # check if there are enough copies for every keyer to be assigned slot 1
    # figure out when to start assigning keyers to slot 2 if not
    if len(reel_qs) < len(keyers):

        break_point = len(keyers) - len(reel_qs)
        print(f"more keyers than reels, break point is {break_point}")
        raise IndexError

    for i in range(min(len(reel_qs), len(keyers))):

        this_keyer = keyers[i]
        this_reel = reel_qs[i]

        assign_reel_to_keyer(this_reel, this_keyer, slot_to_assign)


def refresh_db():
    '''
    INTENDED FOR DEV ONLY
    Convenience function to wipe existing rows and reload Images
    '''
    delete_model_data()
    load_form_fields(settings.FORM_FIELDS_CSV)
    load_reels_from_csv(settings.DEFAULT_REEL_LOAD_SPEC)
    create_1990_dummy_breakers()


def bulk_load_db(shrink_images=False):
    '''
    Function to load form fields, images, and dummy 1990 breakers
    FOR PRODUCTION

    Takes:
    - optional boolean to shrink images prior to loading into DB
    '''

    if shrink_images:
        shrink_reel_images_before_db(settings.DEFAULT_REEL_LOAD_SPEC)

    load_form_fields(settings.FORM_FIELDS_CSV)
    load_reels_from_csv(settings.DEFAULT_REEL_LOAD_SPEC)
    create_1990_dummy_breakers([])
