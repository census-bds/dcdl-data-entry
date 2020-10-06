"""
Module for generating fake data for the models
"""

from EntryApp.models import Image


def generate_n_Images(n, fake_suffix = ''):
    """
    Generate n fake image paths and insert them into DB

    Takes: 
        - int # of paths to generate
        - optional string suffix to append to fake path names
    Returns: None
    """

    fake_paths = ['fake_IMG_' + str(n) + fake_suffix for n in range(0, n)]

    for f in fake_paths:
        img = Image(img_path=f,  is_complete=False,  year=None, image_type=None, date_complete=None)
        img.save()


def delete_fake_Images():
    """
    Delete the fake images from DB
    """
    pass
