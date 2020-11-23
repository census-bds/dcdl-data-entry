"""
Module for generating fake data for the models
"""
from EntryApp import models


def generate_n_Images(n, users, fake_suffix = ''):
    """
    Generate n fake image paths and insert them into DB

    Takes: 
        - int # of paths to generate
        - list of user jbids who will enter data
        - optional string suffix to append to fake path names
    Returns: None
    """

    fake_paths = ['fake_IMG_' + str(n) + fake_suffix for n in range(0, n)] 

    first = True
    for u in users:
        for f in fake_paths:

            if first:
                img = models.Image(img_path=f, \
                                    jbid=u, \
                                    year=1970, \
                                    image_type='breaker', \
                                    is_complete=False, \
                                    date_complete=None)
                first = False

            else:
                img = models.Image(img_path=f, \
                                    jbid=u, \
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


def populate_models(users=['jbid123', 'jbid456']):
    '''
    FOR DEV: Create ten Images for each user and make the first one a Breaker
    '''

    generate_n_Images(10, users)

    for u in users:
        first_img = models.Image.objects.filter(jbid=u)[0]
        b = models.Breaker(img=first_img, jbid=u)
        b.save()


def refresh_db():
    '''
    Refresh the database so Images aren't complete and other tables are empty
    '''

    for m in [models.Record, models.Sheet, models.Breaker, models.Image]:
        rows = m.objects.all()
        for r in rows:
            r.delete()

    populate_models() 

    

