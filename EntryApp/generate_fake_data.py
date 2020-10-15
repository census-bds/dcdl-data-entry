"""
Module for generating fake data for the models
"""

from EntryApp import models


def generate_n_Images(n, fake_suffix = ''):
    """
    Generate n fake image paths and insert them into DB

    Takes: 
        - int # of paths to generate
        - optional string suffix to append to fake path names
    Returns: None
    """

    fake_paths = ['fake_IMG_' + str(n) + fake_suffix for n in range(0, n)]

    first = True
    for f in fake_paths:

        if first:
            img = models.Image(img_path=f, \
                                year=1970, \
                                image_type='breaker', \
                                is_complete=False, \
                                date_complete=None)
            first = False

        else:
            img = models.Image(img_path=f, \
                                is_complete=False, \
                                year=None, 
                                image_type=None, \
                                date_complete=None)
        img.save()


def delete_fake_Image(img_list = ''):
    """
    Delete the fake images from DB 
    Default is to delete all

    Takes: 
    - optional list of img file paths
    Returns:
    - None
    """

    if img_list:
        images = [models.Image.filter(img_file_path=i) for i in img_list]

    else:
        img_list = models.Image.objects.all()
    
    for img in img_list:
        img.delete()


def populate_models():
    '''
    FOR DEV: Create ten Images and make the first one a Breaker
    '''

    generate_n_Images(10)

    first_img = models.Image.objects.all()[0]
    b = models.Breaker(img=first_img)
    b.save()
