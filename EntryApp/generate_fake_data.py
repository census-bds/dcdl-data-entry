"""
Module for generating fake data for the models
"""
from EntryApp.models import Image, Breaker, Sheet, OtherImage, Record, FormField


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
                img = Image(img_path=f, \
                                    jbid=u, \
                                    year=1970, \
                                    image_type='breaker', \
                                    is_complete=False, \
                                    date_complete=None)
                first = False

            else:
                img = Image(img_path=f, \
                                    jbid=u, \
                                    is_complete=False, \
                                    year=None, 
                                    image_type=None, \
                                    date_complete=None)
            img.save()


def delete_data(model):
    """
    Delete data from a model

    Takes: 
    - model object
    Returns:
    - None
    """

    data = model.objects.all()
    for d in data:
        d.delete()


def populate_models(users=['jbid123', 'jbid456']):
    '''
    FOR DEV: Create ten Images for each user and make the first one a Breaker
    '''

    generate_n_Images(10, users)

    for u in users:
        first_img = Image.objects.filter(jbid=u)[0]
        b = Breaker(img=first_img, jbid=u)
        b.save()


def refresh_db():
    '''
    Refresh the database so Images aren't complete and other tables are empty
    '''

    for m in [Record, Sheet, Breaker, Image]:
        rows = m.objects.all()
        for r in rows:
            r.delete()

    populate_models() 

    
#================================#
# GENERATE FIXTURE IN JSON
#================================#

def generate_image_json():
    '''
    Generate image records in JSON for use as fixture for testing
    '''
    pass