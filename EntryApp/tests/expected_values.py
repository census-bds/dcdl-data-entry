"""
EXPECTED VALUES FOR TESTING

This module contains data dictionaries with the values expected or used
in test_views.
"""


DATA = {
    'fixtures/dev_data_2022-07-05.json':
        {'jbid789':
            {
                'lf_type_form_values': {
                    'image_id': 833,
                },
                'lf_type_entry': {
                    'image_id': 833,
                    'action': 'update_image',
                    'image_type': 'longform'
                },
                'lf_data_entry': {
                    'image_id': 833,
                    'action': 'update_longform',
                    'user': 'jbid789',
                    'longform_id': 3,
                    'serial_no': '123456789',
                    'person_no': 1,
                    'employer': 'Census',
                    'industry': 'government',
                }
            },
        'jbid456': 
            {
                'test_1960_hard_to_read_checkbox': {
                    'image_id': 736,
                },
            },
        'jbid123':
            {
                'current_image_file_id': 1716,
                'current_img_id': 767,
                'current_reel_id': 191,
                'current_reel_name': 'dev_1970',
                'year': 1970,
                'img_url': '/images/1970/dev_1970/test_image_30_smaller_smaller_smaller.jpg',
                'code_image_test_a_context': {
                    'image_id': 767,
                    'image_form_values': {'year': 1970, 'image_type': ''}, 
                    'username': 'jbid123', 
                    'user': 'jbid123',
                    'slug': 'test_image_32.jpg', 
                    'year': 1970
                },
                'code_image_test_sheet_already_exists': {
                    'action': 'update_sheet_type',
                    'image_id': 766,
                    'username': 'jbid123', 
                    'user': 'jbid123', 
                    'jbid': 'jbid123', 
                    'year': 1970,
                    # 'sheet_id': 20,
                },
                'code_image_test_sheet_has_no_breaker': {
                    'action': 'update_sheet_type',
                    'image_id': 767,
                    'username': 'jbid123', 
                    'user': 'jbid123', 
                    'jbid': 'jbid123',
                    'year': 1970,
                },
                'image_type_options': [
                    '<input type="radio" name="image_type" value="breaker"',
                    '<input type="radio" name="image_type" value="sheet"',
                    '<input type="radio" name="image_type" value="other"',
                ],
                'image_type_breaker_post': {
                    'action': 'update_image',
                    'image_id': 767,
                    'image_type': 'breaker',
                },
                'image_type_other_post': {
                    'action': 'update_image',
                    'image_id': 769,
                    'image_type': 'other',                
                },
                'image_type_sheet_post': { 
                    'action': 'update_image',
                    'image_id': 767,
                    'image_type': 'sheet',                
                },
                'breaker_data_entry': {
                    'action': '',
                    'image_id': 765,
                    'year': 1970,
                    'state': 'OH',
                },
                'sheet_data_entry': {
                    'action': 'update_sheet_type',
                    'image_id': 766,
                    'user': 'jbid456',
                    'jbid': 'jbid456',
                    'year': 1970, 
                    'num_records': '1',
                    'sheet_id': 20
                },
                'report_problem': {
                    'image_id': 768,
                    'problem': ['on'],
                    'description': ['foo bar baz'],
                }
            },
        }
    }