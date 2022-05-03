
DATA = {
    'fixtures/dev_data_20220503_1110.json':
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
                'current_image_file_id': 176,
                'current_img_id': 161,
                'current_reel_id': 26,
                'current_reel_name': 'dev_1960',
                'year': 1960,
                'img_url': '/images/1960/dev_1960/fake_IMG_2_smaller.jpg',
                'code_image_test_a_context': {
                    'image_id': 162,
                    'image_form_values': {'year': 1960, 'image_type': ''}, 
                    'username': 'jbid456', 
                    'user': 'jbid456',
                    'slug': 'fake_IMG_3_smaller.jpg', 
                    'param_names': {'PARAM_NAME_ACTION': 'action', 'PARAM_NAME_BREAKER_ID': 'breaker_id', 'PARAM_NAME_IMAGE_ID': 'image_id', 'PARAM_NAME_IMAGE_TYPE': 'image_type', 'PARAM_NAME_LONGFORM_ID': 'longform_id', 'PARAM_NAME_OTHER_IMAGE_ID': 'other_image_id', 'PARAM_NAME_RECORD_ID': 'record_id', 'PARAM_NAME_SHEET_ID': 'sheet_id', 'PARAM_NAME_YEAR': 'year'},
                    'year': 1960 
                },
                'code_image_test_f_sheet_integrity_error': {
                    'action': 'update_sheet_type',
                    'image_id': 161,
                    'username': 'jbid456', 
                    'user': 'jbid456', 
                    'jbid': 'jbid456', 
                    'year': 1960 
                },
                'image_type_options': [
                    '<input type="radio" name="image_type" value="breaker"',
                    '<input type="radio" name="image_type" value="sheet"',
                    '<input type="radio" name="image_type" value="other"',
                ],
                'image_type_breaker_post': {
                    'action': 'update_image',
                    'image_id': 163,
                    'image_type': 'breaker',
                },
                'image_type_other_post': {
                    'action': 'update_image',
                    'image_id': 163,
                    'image_type': 'other',                
                },
                'image_type_sheet_post': {
                    'action': 'update_image',
                    'image_id': 163,
                    'image_type': 'sheet',                
                },
                'breaker_data_entry': {
                    'action': '',
                    'image_id': 160,
                    # 'breaker_id': 24,
                    'year': 1960,
                    'state': 'OH',
                },
                'sheet_data_entry': {
                    'action': 'update_sheet_type',
                    'image_id': 162,
                    'user': 'jbid456',
                    'jbid': 'jbid456',
                    'year': 1960, 
                    'num_records': '4',
                    'sheet_id': 11
                },
                'report_problem': {
                    'image_id': 163
                }
            },
        },
    }
