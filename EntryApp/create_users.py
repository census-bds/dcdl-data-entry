#===============================================================#
# SET UP AN ADMIN, DATA ENTRY GROUP AND USERS
#===============================================================#

import os
import pathlib
import pandas as pd

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.hashers import make_password
from EntryApp.models import Image



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
        user, _ = User.objects.get_or_create(
            username=jbids.pop(),
            password=make_password(pws.pop())
        )
        group_id = Group.objects.get(name='data_entry').id
        user.groups.add(group_id)
        user.save()


def add_entry_user(jbid, pw):
    '''
    Create a new user and add to the data entry group

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
