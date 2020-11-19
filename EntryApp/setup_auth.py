#===============================================================#
# SET UP AN ADMIN, DATA ENTRY GROUP AND USERS
#===============================================================#

from django.contrib.auth.models import User, Group
from EntryApp.models import Image


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


def add_entry_user(jbid, pw):
    '''
    Add a new user to the data entry group
    Populate Image model with blank records for that user

    Takes:
    - string username (jbid)
    - string password 
    Returns:
    - None
    '''

    pass
