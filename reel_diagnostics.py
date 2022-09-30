import argparse
import glob
import os
import pandas as pd
import re

"""
This module counts the number of images in reels and identifies
any missing or strangely sized images.
"""

pd.set_option('max_rows', 50)
pd.set_option('max_columns', 150)
pd.set_option('mode.chained_assignment', None)


def check_image_order(image_list, image_regex='[0-9]{4}(?=_smaller.jpg)'):
    '''
    Check if image filenames monotonically increase by one with no gaps

    Takes:
    - list of images (should come in sorted)
    - regex to get image number from filename 
    Returns:
    - boolean indicating whether there's any missing images
    - list of missing (empty if there are none)
    '''

    if len(image_list) == 0:
        return False, []

    first_image = image_list[0]
    last_image = image_list[-1]

    # construct list of expected image numbers
    start_index = int(re.findall(image_regex, first_image)[0])
    stop_index = int(re.findall(image_regex, last_image)[0])
    ordered_indices = list(range(start_index, stop_index + 1))
        
    # construct list of actual image numbers
    image_indices = [int(re.findall(image_regex, i)[0]) for i in image_list]

    # compare
    missing = list(set(ordered_indices).difference(image_indices))

    return len(missing) == 0, missing


def count_abnormally_sized_files(image_list):
    '''
    Check for image file sizes that are abnormally small/large, which
    might indicate a problem with scan quality

    Takes:
    - list of images
    Returns:
    - count of very small images
    - count of very large images
    '''

    too_small = 0
    too_big = 0

    for i in image_list:

        try:
            size = os.path.getsize(i)

            if size < 100000:
                too_small += 1
            elif size > (20 * 100000):
                too_big += 1
            else:
                continue

        except OSError:

            print("Problem getting file size of {i}".format(i=i))

    return too_small, too_big


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Count images in reels and check for anomalies.')
    parser.add_argument( '-i', '--path-in', help='path down which to look', dest='path_in')
    parser.add_argument( '-o', '--path-out', help='path for output file', dest='path_out')
    args = parser.parse_args()

    path_in = args.path_in
    path_out = args.path_out

    parent_dir_contents = os.listdir(path_in)
    dir_list = [d for d in parent_dir_contents if os.path.isdir(path_in + d)]

    # what we want to know
    # - how many full size images there are
    # - how many smaller images there are
    # - are images all in order or are there some missing?
    # - are there any suspiciously small images?

    output = {
        'path': [],
        'num_images_in_directory': [],
        'num_smaller_images_in_directory': [],
        'image_numbers_have_no_gaps': [],
        'num_missing': [],
        'num_suspiciously_small': [],
        'num_suspiciously_large': [],
        # 'missing_id': [],
        # 'too_small_id': []
    }

    for d in dir_list:  

        path_to_dir = path_in + d
        all_images = sorted(glob.glob(path_to_dir + '/*.jpg'))
        smaller_images = sorted(glob.glob(path_to_dir + "/*_smaller.jpg"))

        any_missing, missing = check_image_order(smaller_images)

        output['path'].append(path_to_dir)
        output['num_images_in_directory'].append(len(all_images))
        output['num_smaller_images_in_directory'].append(len(smaller_images))
        output['image_numbers_have_no_gaps'].append(any_missing)
        output['num_missing'].append(len(missing))

        too_small, too_big = count_abnormally_sized_files(smaller_images)
        output['num_suspiciously_small'].append(too_small)
        output['num_suspiciously_large'].append(too_big)

        # TODO
        # output['missing_id'].append('')
        # output['too_small_id'].append('')
        
    results = pd.DataFrame.from_dict(output)

    results.to_csv(path_out, index=False)
