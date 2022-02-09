#===============================================================#
# REDUCE THE SIZE OF IMAGES TO HELP APP LOAD SPEEDS
# 2022-02-08
#===============================================================#

from PIL import Image

from EntryApp.models import ImageFile
from EntryApp.models import Reel


# OUTLINE OF PLAN:
# - query DB to get a list of all the ImageFile filepaths
# - use this list to read each ImageFile in
# - use Image.resize() to reduce size by ~half
# - save file with the same name but _smaller appended

def shrink_image(image_file_path, out_path_suffix = "_smaller"):
    '''
    Reduce the size of an image by half and save it with new name

    Takes:
    - string filepath to image file
    - optional suffix (default is _smaller)
    Returns:
    - None
    '''

    image = Image.open(image_file_path)

    # cut size in half
    new_dimensions = (image.size[0] // 2, image.size[1] // 2)
    half_size = image.resize(new_dimensions, Image.ANTIALIAS)

    # save with new name
    out_name = image_file_path.strip(".jpg") + out_path_suffix + ".jpg"
    half_size.save(out_name, optimize=True, quality=30)


def apply_shrink_to_images():
    '''
    Method to loop through all ImageFiles and shrink them

    Takes: None
    Returns: None
    '''

    image_file_qs = ImageFile.objects.all()

    for i in image_file_qs:
        shrink_image(i.img_path)

