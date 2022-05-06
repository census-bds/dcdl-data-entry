import requests

from bs4 import BeautifulSoup
from datetime import datetime

import dcdl.settings as settings

"""
Load test script to make GET and POST requests to test server ability
to handle more concurrent users.
"""

def make_url(page_name):
    '''
    Get the url for a given view for the app instance in settings.py

    Takes:
    - name of page as string
    Returns:
    - string url
    '''

    instance = settings.APP_INSTANCE

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
        # headers=header_data,
    )

    return post


if __name__ == '__main__':

    s = requests.Session()

    # URLs
    index_url = make_url('')
    code_image_url = make_url('code-image/')

    ##### GET AUTHENTICATED

    # make a GET to get the CSRF token cookie
    login_get = s.get('http://localhost:7002/accounts/login')

    csrf_token = get_csrf_from_html(login_get.content)
    print("CSRF token from content is", csrf_token)

    post_data = {
        'csrfmiddlewaretoken': csrf_token,
        'username':'jbid123',
        'password': 'dcdl1980',
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
    post = make_post(s, code_image_url, {'image_id': '45'})

    # update image type
    image_data = {
        'image_id': '45',
        'image_type': 'sheet',
        'action': 'update_image',
    }
    post2 = make_post(s, code_image_url, image_data)

    # update sheet info
    sheet_data = {
        'image_id': '45',
        'action': 'update_sheet_type',
        'num_records': 12,
    }
    post3 = make_post(s, code_image_url, sheet_data)

    # add record info
    record_data = {
        'image_id': '45',
        'sheet_id': '7',
        'action': 'update_record',
        'last_name': 'Frank',
        'first_name': 'T',
        'age': 97
    }
    post4 = make_post(s, code_image_url, record_data)

    # mark image as complete
    complete_data = {
        'image_id': '45',
        'sheet_id': '7',
        'action': 'complete_image'
    }
    post5 = make_post(s, code_image_url, complete_data)