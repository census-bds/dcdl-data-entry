import argparse
import requests

from bs4 import BeautifulSoup
from datetime import datetime

# import dcdl.settings as settings

"""
Load test script to make GET and POST requests to test server ability
to handle more concurrent users.
"""

USER_INFO = {
    'jbid123': {
        'username': 'jbid123',
        'password': 'dcdl1980',
        'image_id': '45',
        'sheet_id': '7',
        'num_records': '12',
        'last_name': 'Frank',
        'first_name': 'T',
        'age': 97,
    },
    'jbid456': {
        'username': 'jbid456',
        'password': 'dcdl1980',
        'image_id': '48',
        'sheet_id': '99',
        'num_records': '11',
        'last_name': 'F',
        'first_name': 'T',
        'age': 97,
    },
    'jbid789': {
        'username': 'jbid789',
        'password': 'dcdl1980',
        'image_id': '52',
        'sheet_id': '12',
        'num_records': '11',
        'last_name': 'T',
        'first_name': 'F',
        'age': 97,
    },
    'jbid999': {
        'username': 'jbid999',
        'password': 'genadek001',
        'image_id': '49',
        'sheet_id': '16',
        'num_records': '11',
        'last_name': 'F',
        'first_name': 'T',
        'age': 97,
    },
}



def make_url(page_name):
    '''
    Get the url for a given view for the app instance in settings.py

    Takes:
    - name of page as string
    Returns:
    - string url
    '''

    instance = "test" #settings.APP_INSTANCE

    if instance == 'dev':
        return 'http://localhost:8002/EntryApp/' + page_name

    elif instance == 'test':
        return 'http://localhost:7002/EntryApp/' + page_name

    elif instance == "training":
        return 'http://localhost:7000/EntryApp' + page_name

    elif instance == "production":
        return 'http://localhost:8000/EntryApp' + page_name

    else:
        return


def get_csrf_from_html(html):
    '''
    Extract CSRF token from html

    Takes:
    - html as string, e.g. from response.content
    Returns:
    - csrf token as string
    '''

    soup = BeautifulSoup(html, 'html.parser')
    found = soup.form.find('input', {'name': 'csrfmiddlewaretoken'})
    return found['value']


def make_post(s, url, extra_data={}):
    '''
    Make a post request with optional extra data

    Takes:
    - logged-in session object (requests.Session())
    - string url to POST
    - optional dict of additional data
    Returns:
    - POST response object
    '''

    get = s.get(url)

    # header_csrftoken = get.cookies['csrftoken']
    page_csrftoken = get_csrf_from_html(get.content)

    # header_data = {
    #     'X-CSRFToken': header_csrftoken
    # }
    auth_data = {
        'csrfmiddlewaretoken': page_csrftoken,
        'username':'jbid123',
        'password': 'dcdl1980',
    }
    post_data = {**auth_data, **extra_data}

    # POSTS
    post = s.post(
        'http://localhost:7002/EntryApp/code-image/',
        data=post_data,
    )

    return post


if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Get username input')
    parser.add_argument('username', 
                        help='keyer username')

    args = parser.parse_args()
    jbid = args.username

    # timing
    start_time = datetime.now()

    s = requests.Session()

    # get user
    user_info = USER_INFO[jbid]

    # URLs
    index_url = make_url('')
    code_image_url = make_url('code-image/')

    ##### GET AUTHENTICATED

    # make a GET to get the CSRF token cookie
    login_get = s.get('http://localhost:7002/accounts/login')

    csrf_token = get_csrf_from_html(login_get.content)

    post_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username': user_info['username'],
        'password': user_info['password']
    }

    # now POST to login
    login = s.post(
        'http://localhost:7002/accounts/login/', 
        data=post_data,
    )

    ##### START MAKING REQUESTS

    # GETS
    index_get = s.get(index_url)
    code_image_get = s.get(code_image_url)
    
    # POSTS 
    post = make_post(s, code_image_url, {'image_id': user_info['image_id']})

    # update image type
    image_data = {
        'image_id': user_info['image_id'],
        'image_type': 'sheet',
        'action': 'update_image',
    }
    post2 = make_post(s, code_image_url, image_data)

    # update sheet info
    sheet_data = {
        'image_id': user_info['image_id'],
        'action': 'update_sheet_type',
        'num_records':  user_info['num_records'],
    }
    post3 = make_post(s, code_image_url, sheet_data)

    # add record info
    record_data = {
        'image_id':  user_info['image_id'],
        'sheet_id':  user_info['sheet_id'],
        'action': 'update_record',
        'last_name':  user_info['last_name'],
        'first_name': user_info['first_name'],
        'age':  user_info['age'],
    }
    post4 = make_post(s, code_image_url, record_data)

    # mark image as complete
    complete_data = {
        'image_id':  user_info['image_id'],
        'sheet_id':  user_info['sheet_id'],
        'action': 'complete_image'
    }
    post5 = make_post(s, code_image_url, complete_data)

    finish_time = datetime.now()

    print("run time:",  finish_time-start_time)