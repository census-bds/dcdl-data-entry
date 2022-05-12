
DATA = {
    'fixtures/dev_data_2022-05-12.json':
        {'jbid123':
            {
                'current_image_file_id': 174,
                'current_img_id': 158,
                'current_reel_id': 29,
                'img_url': '/images/1990/dev_1990/test_image_29_smaller.jpg',
                'sheet_type_breaker_post': {
                    'action': 'update_image',
                    'image_id': 158,
                    'image_type': 'breaker',
                },
                'sheet_type_other_post': {
                    'action': 'update_image',
                    'image_id': 158,
                    'image_type': 'other',                
                },
                'sheet_type_sheet_post': {
                    'action': 'update_image',
                    'image_id': 158,
                    'image_type': 'sheet',                
                }
            },
        'jbid456':
            {
                'current_image_file_id': 307,
                'current_img_id': 271,
                'current_reel_id': 37,
                'current_reel_name': 'dev_1970',
                'year': 1970,
                'img_url': '/images/1970/dev_1970/test_image_30_smaller_smaller.jpg',
                'code_image_test_a_context': {
                    'image_id': 272,
                    'image_form_values': {'year': 1970, 'image_type': ''}, 
                    'username': 'jbid456', 
                    'user': 'jbid456',
                    'slug': 'test_image_32.jpg', 
                    'param_names': {'PARAM_NAME_ACTION': 'action', 'PARAM_NAME_BREAKER_ID': 'breaker_id', 'PARAM_NAME_IMAGE_ID': 'image_id', 'PARAM_NAME_IMAGE_TYPE': 'image_type', 'PARAM_NAME_LONGFORM_ID': 'longform_id', 'PARAM_NAME_OTHER_IMAGE_ID': 'other_image_id', 'PARAM_NAME_RECORD_ID': 'record_id', 'PARAM_NAME_SHEET_ID': 'sheet_id', 'PARAM_NAME_YEAR': 'year'},
                    'year': 1970
                },
                'code_image_test_f_sheet_integrity_error': {
                    'action': 'update_sheet_type',
                    'image_id': 271,
                    'username': 'jbid456', 
                    'user': 'jbid456', 
                    'jbid': 'jbid456', 
                    'year': 1970,
                    'sheet_id': 13,
                },
                'image_type_options': [
                    '<input type="radio" name="image_type" value="breaker"',
                    '<input type="radio" name="image_type" value="sheet"',
                    '<input type="radio" name="image_type" value="other"',
                ],
                'image_type_breaker_post': {
                    'action': 'update_image',
                    'image_id': 270,
                    'image_type': 'breaker',
                },
                'image_type_other_post': {
                    'action': 'update_image',
                    'image_id': 273,
                    'image_type': 'other',                
                },
                'image_type_sheet_post': { 
                    'action': 'update_image',
                    'image_id': 272,
                    'image_type': 'sheet',                
                },
                'breaker_data_entry': {
                    'action': '',
                    'image_id': 270,
                    # 'breaker_id': 24,
                    'year': 1970,
                    'state': 'OH',
                },
                'sheet_data_entry': {
                    'action': 'update_sheet_type',
                    'image_id': 271,
                    'user': 'jbid456',
                    'jbid': 'jbid456',
                    'year': 1970, 
                    'num_records': '1',
                    'sheet_id': 13
                },
                'report_problem': {
                    'image_id': 271,
                    'problem': ['on'],
                    'description': ['foo bar baz'],
                }
            },
        },
    }
