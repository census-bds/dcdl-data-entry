#===============================================================#
# REDUCE THE SIZE OF IMAGES TO HELP APP LOAD SPEEDS
# 2022-02-08
#===============================================================#

import argparse
from contextlib import contextmanager
import os
import pathlib
import psycopg2 as pg

from PIL import Image

import dcdl.settings as settings

# by default, pgpass file gets created in cwd
# (in case of this script, project root)
PGPASS_PATH = os.path.join(pathlib.Path().resolve(), ".pgpass")


@contextmanager
def pgpass_context(db_settings):


    """
    In order to supply password, postgres requires a ~/.pgpass file.
    https://stackoverflow.com/questions/2893954/how-to-pass-in-password-to-pg-dump

    This context manager creates that file and then deletes when script ends
    (or dies).

    Note: if you have a ~/.pgpass file, this script will die and warn you.

    """

    if os.path.exists(PGPASS_PATH):
        raise KeyError("the .pgpass file exists, move before running this.")

    pgpass_str = "{host}:{port}:*:{user}:{password}\n"\
        .format(host=db_settings["HOST"],
                port=db_settings["PORT"],
                user=db_settings["USER"],
                password=db_settings["PASSWORD"])

    with open(PGPASS_PATH, "w+") as pgpass_f:
        pgpass_f.write(pgpass_str)

    os.chmod(PGPASS_PATH, 0o600)

    try:
        yield
    finally:
        os.remove(PGPASS_PATH)



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
    half_size.save()