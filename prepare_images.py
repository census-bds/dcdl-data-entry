import argparse
import glob
import os
import pandas as pd


from EntryApp.shrink_images import shrink_reel_images_before_db


"""
This module handles the process of shrinking images and removing the 
full-size versions.

It will:
- look through a directory and provide a count of full size images
- shrink those images
- provided a count of shrunken images
- remove full size images
- provide a final count of images in directory
"""

FILE_SIZE_THRESHOLD = 2000000



def shrink_wrapper(dir_name):
    '''
    Wraps shrink method from EntryApp.shrink_images to give it a try/except

    Takes:
    - directory name
    Returns:
    - boolean based on success of shrinking
    '''

    try:
        shrink_reel_images_before_db(dir_name)
        print(f"\t\tShrunk images in {dir_name}.")

        return True

    except Exception as e:
        print(e)

        return False


def remove_fullsize_images(dir_name):
    '''
    Deletes the full-size copies of images from a specified directory

    Takes:
    - directory filepath
    Returns: None
    '''

    all_images = [dir_name + '/' + i for i in os.listdir(dir_name)]
    images_to_remove = [i for i in all_images if os.path.getsize(i) > FILE_SIZE_THRESHOLD]

    for i in images_to_remove:
        os.remove(i)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Shrink images and remove full size versions')
    parser.add_argument( '-p', '--path', help='path down which to look', dest='filepath')
    args = parser.parse_args()

    start_filepath = args.filepath

    parent_dir_contents = os.listdir(start_filepath)
    dir_list = [d for d in parent_dir_contents if os.path.isdir(start_filepath + d)]

    for d in dir_list:

        path_to_dir = start_filepath + d
        num_images = len(glob.glob(path_to_dir + '/*.jpg'))
        num_smaller_images = len(glob.glob(d + "/*_smaller.jpg"))

        print(f"Reel directory {d} has {num_smaller_images} shrunk images out of {num_images}.")


        if num_images == 0:

            print(f"\tDirectory {d} has no images inside it. Can't do anything here.")


        elif num_images > 0 and num_smaller_images == 0:

            print(f"\tDirectory {d} has {num_images} but it looks like we haven't shrunk them yet.")
            shrunk_success = shrink_wrapper(path_to_dir)

            if shrunk_success:

                remove_fullsize_images(path_to_dir)


        elif num_images == num_smaller_images:

            print(f"\tDirectory {d} image counts look good, moving on.")


        elif num_images == 2 * num_smaller_images:

            print(f"\tDirectory {d} has 2x as many big images as small ones.")
            remove_fullsize_images(path_to_dir)
        
        else:

            print(f"\Directory {d} has an unexpected number of images. Please go look.")
