#===============================================================#
# REDUCE THE SIZE OF IMAGES TO HELP APP LOAD SPEEDS
# 2022-02-08
#===============================================================#

import os
from PIL import Image

from EntryApp.models import ImageFile
from EntryApp.models import Reel


def make_new_filepath(image_file_path, suffix = "_smaller"):
    '''
    Takes the existing image file path and appends suffix

    Takes:
    - string filepath to image file
    - optional suffix (default is _smaller)
    Returns:
    - None
    '''

    out_path = image_file_path.strip(".jpg") + suffix + ".jpg"
    out_name = out_path.split("/")[-1]

    return out_path, out_name


def shrink_image(image_file_path, out_path):
    '''
    Reduce the size of an image by half and save it with new name

    Takes:
    - string filepath to image file
    - optional suffix (default is _smaller)
    Returns:
    - None
    '''

    #  # skip this if compressed image already exists
    # if os.path.isfile(out_path):
    #     return

    try:
        image = Image.open(image_file_path)

        # cut size in half
        new_dimensions = (image.size[0] // 2, image.size[1] // 2)
        half_size = image.resize(new_dimensions, Image.ANTIALIAS)

        # save with new name
        half_size.save(out_path, optimize=True, quality=70)

    except Exception as e:
        print("Exception in shrink_image():", e)

    return



def apply_shrink_to_images(image_file_qs = None):
    '''
    Method to loop through all ImageFiles and shrink them

    Takes: optional queryset of images
    Returns: None
    '''

    if not image_file_qs:
        image_file_qs = ImageFile.objects.all()

    for i in image_file_qs:

        new_out_path, new_out_name = make_new_filepath(i.img_path)

        try:
            shrink_image(i.img_path, new_out_path)
            i.smaller_image_file_name = new_out_name
            i.save()
        
        except Exception as e:
            print(e)

