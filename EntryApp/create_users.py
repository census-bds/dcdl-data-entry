#===============================================================#
# SET UP AN ADMIN, DATA ENTRY GROUP AND USERS
#===============================================================#

import os
import pathlib
import pandas as pd

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from EntryApp.models import Image
from EntryApp.models import Keyer



def create_entry_group():
    '''
    Create a group for entry users (no extra permissions)

    Takes: 
    - None
    Returns:
    - None
    '''

    group, _ = Group.objects.get_or_create(name='data_entry')


def add_entry_user(jbid, pw):
    '''
    Create a new user and add to the data entry group

    Takes:
    - string username (jbid)
    - string password 
    Returns:
    - None
    '''

    this_user = User.objects.create_user(
        username=jbid,
        password=pw
    )
    group_id = Group.objects.get(name='data_entry').id
    this_user.groups.add(group_id)
    this_user.save()        

    this_keyer, _ = Keyer.objects.get_or_create(
        user = this_user,
        jbid = jbid,
        reel_count = 0
    )


def bulk_load_entry_users(path=settings.USER_INFO):
    '''
    Create entry users from a csv file 

    Takes:
    - string filepath to csv
    Returns:
    - None
    '''

    df = pd.read_csv(path)
    df.apply(lambda x: add_entry_user(x.jbid, x.password), axis=1)    