"""
Module for generating fake data for the models
"""
from django.contrib.auth.models import User, Group
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

#================================#
# ADMIN / USER/ GROUPS
#================================#

def create_admin(pw, username='admin', email=None):
    '''
    Sets up an admin

    Takes:
    - string password (required)
    - string username (default is admin)
    - string email (optional) 
    '''

    admin = User.objects.create_superuser(username, password=password, email=email)
    admin.save()


def create_entry_group():
    '''
    Create a group for users with data entry permissions
    '''

    data_models = ['Image', 'Sheet', 'Breaker', 'Record', 'CurrentEntry']
    perms = []

    for d in data_models:
        for p in ['add', 'change', 'view']
        perms.append(f'EntryApp.{p}_{d}')

    print("data_entry permission list: \n\t", perms)

    group = Group(name='data_entry')
    group.permissions.set(perms)
    group.save()


def create_entry_users(jbids=['jbid123', 'jbid456'], pws=['dcdl1980', 'dcdl1980']):
    '''
    Create data entry users 

    Takes:
    - list of strings of usernames (jbids)
    - list of strings of passwords 
    '''

    if len(jbids) != len(pws):
        print("List of usernames must be the same length as list of passwords.")
        raise ValueError

    while jbids:
        user = User.objects.create_user(username=jbids.pop(), password=pwd.pop())
        user.groups.add('data_entry')
        user.save()