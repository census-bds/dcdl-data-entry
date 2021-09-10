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

        this_jbid = jbids.pop()

        this_user, _ = User.objects.get_or_create(
            username=this_jbid,
            password=make_password(pws.pop())
        )
        group_id = Group.objects.get(name='data_entry').id
        this_user.groups.add(group_id)
        this_user.save()

        this_keyer, _ = Keyer.objects.get_or_create(
            user = this_user,
            jbid = this_jbid,
            reel_count = 0
        )


def add_entry_user(jbid, pw):
    '''
    Create a new user and add to the data entry group

    Takes:
    - string username (jbid)
    - string password 
    Returns:
    - None
    '''

    this_user, _ = User.objects.get_or_create(
        username=jbid,
        password=make_password(pw)
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