"""
SET UP AN ADMIN, DATA ENTRY GROUP AND USERS

This module contains methods to add authorized keyers. Specifically, these
methods set up a data entry auth group, add users to that group, and 
populate the Keyer model.

It is intended to be used in the django shell along with a csv file 
containing keyer information.
"""

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
    Create a group for entry users (no extra permissions, just convenience)

    Takes: 
    - None
    Returns:
    - None
    '''

    group, _ = Group.objects.get_or_create(name='data_entry')


def add_entry_user(jbid, pw):
    '''
    Create a new user and add to the data entry group. Also, add that user
    to the Keyer model.

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
    Create entry users from a csv file, wrapping add_entry_user().
    
    The default argument is a csv path set in the django settings.py file.
    For an example of how this csv should be formatted, see
    example_user_info.csv. 

    Takes:
    - string filepath to csv
    Returns:
    - None
    '''

    df = pd.read_csv(path)
    df.apply(lambda x: add_entry_user(x.jbid, x.password), axis=1)    