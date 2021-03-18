#===============================================================#
# SET UP AN ADMIN, DATA ENTRY GROUP AND USERS
#===============================================================#

import os
import pathlib
import pandas as pd

from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.hashers import make_password
from EntryApp.models import Image

# expects the csv with user data to be in root of project (git repo level)
USER_INFO = os.path.join(pathlib.Path(__file__).parent.parent.absolute(), 'user_info.csv')

DATA_MODELS = [
        'breaker',
        # 'current entry',
        'image',
        'sheet',
        'record',
        # 'other image'
    ]


def create_entry_group(data_models=DATA_MODELS):
    '''
    Create a group for users with data entry permissions
    Assumes that the add, change, and view permission exists for each model

    Takes: 
    - list of model names as string in lowercase with spaces
    Returns:
    - None
    '''

    # first create the group
    group, _ = Group.objects.get_or_create(name='data_entry')
    
    for d in data_models:
        for p in ['add', 'change', 'view']:
            print(f'can_{p}_{d}')
            perm = Permission.objects.get(
                codename=f'can_{p}_{d}'
            )
            group.permissions.add(perm)
    group.save()


def create_entry_users(jbids=['jbid123', 'jbid456'], pws=['dcdl1980', 'dcdl1980']):
    '''
    Create data entry users (testing fn mostly)

    Takes:
    - list of strings of usernames (jbids)
    - list of strings of passwords 
    Returns:
    - None
    '''

    if len(jbids) != len(pws):
        print("List of usernames must be the same length as list of passwords.")
        raise ValueError

    while jbids:
        user, _ = User.objects.get_or_create(
            username=jbids.pop(),
            password=make_password(pws.pop())
        )
        group_id = Group.objects.get(name='data_entry').id
        user.groups.add(group_id)
        user.save()


def add_entry_user(jbid, pw):
    '''
    Add a new user to the data entry group
    Option to populate Image model with blank records for that user

    Takes:
    - string username (jbid)
    - string password 
    Returns:
    - None
    '''

    user, _ = User.objects.get_or_create(
        username=jbid,
        password=make_password(pw)
    )
    group_id = Group.objects.get(name='data_entry').id
    user.groups.add(group_id)
    user.save()        


def bulk_load_entry_users(path=USER_INFO):
    '''
    NOT WORKING YET - Create entry users from a csv file 

    Takes:
    - string filepath to csv
    Returns:
    - None
    '''

    df = pd.read_csv(path)
    df.apply(lambda x: add_entry_user(x.jbid, x.password), axis=1)


# import EntryApp.create_users as users

