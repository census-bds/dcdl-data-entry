import argparse
import glob
import os
import pandas as pd
import re
import shutil

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



def shrink_wrapper(dir_name, num_images):
    '''
    Wraps shrink method from EntryApp.shrink_images to give it a try/except

    Takes:
    - directory name
    - expected number of images
    Returns:
    - boolean based on success of shrinking
    '''

    # get # of images here, so we can see if we're mid-copy
    current_image_count = len([dir_name + '/' + i for i in os.listdir(dir_name)])
   
    if current_image_count != num_images:

        print(f"\tNumber of images is changing; doing nothing.")

        return False


    try:
        shrink_reel_images_before_db(dir_name)
        print(f"\tShrunk images in {dir_name}.")

        return True

    except Exception as e:
        print(e)

        return False


def remove_fullsize_images(dir_name, num_images):
    '''
    Deletes the full-size copies of images from a specified directory

    Takes:
    - directory filepath
    - expected # of images to remove 
    Returns: None
    '''

    all_images = [dir_name + '/' + i for i in os.listdir(dir_name)]
    images_to_remove = [i for i in all_images if re.search('[0-9].jpg$', i)]

    print(f"\tChecking image counts: {len(all_images)} should be 2x {len(images_to_remove)}")
    assert len(images_to_remove) == (len(all_images) / 2)

    for i in images_to_remove:
        os.remove(i)
        
    print(f"\tRemoved {len(images_to_remove)}.")


def copy_small_images(dir_name, dest):
    '''
    Move the shrunken images from original directory to destination 
    directory. Only called if destination argument provided.

    Takes:
    - directory filepath
    - destination parent directory filepath
    Returns: None
    '''

    destination = dest + dir_name.split("/")[-1] + "/"
    print(f"\tMoving images from {dir_name} to {destination}...")

    # check if destination directory exists and contains files; create if not
    if os.path.isdir(destination):

        print(f"\tDestination directory {destination} already exists.")

        if len(glob.glob(destination + "*.jpg")) != 0:

            print(f"\tDestination directory already contains images. Skipping.")

            return

    else:

        print(f"\tCreating destination directory {destination}...")
        os.mkdir(destination)

    small_images_orig_path = glob.glob(dir_name + "/" + "*_smaller.jpg")
    # print(f"small_images_orig_path is {small_images_orig_path[:10]}")

    small_images_new_path = [destination + i.split("/")[-1] for i in small_images_orig_path]
    # print(f"small_images_new_path is {small_images_new_path[:10]}")

    print(f"\tPreparing to move {len(small_images_orig_path)} images...")

    for old, new in zip(small_images_orig_path, small_images_new_path):
        shutil.copy(old, new)

    print(f"\tMoved {len(small_images_orig_path)}.")

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Shrink images and remove full size versions')
    parser.add_argument( '-p', '--path', help='path down which to look', dest='filepath')
    parser.add_argument( '-d', '--destination', help='destination to move small images to', dest='destination')
    args = parser.parse_args()

    start_filepath = args.filepath
    dest = args.destination

    parent_dir_contents = os.listdir(start_filepath)
    dir_list = [d for d in parent_dir_contents if os.path.isdir(start_filepath + d)]

    for d in dir_list:

        path_to_dir = start_filepath + d
        num_images = len(glob.glob(path_to_dir + '/*.jpg'))
        num_smaller_images = len(glob.glob(path_to_dir + "/*_smaller.jpg"))

        print(f"Reel directory {d} has {num_smaller_images} shrunk images out of {num_images}.")

        # case 1: no images have been copied here yet
        if num_images == 0:

            print(f"\tDirectory {d} has no images inside it. Can't do anything here.")

        # case 2: images have been copied, but not shrunk
        elif num_images > 0 and num_smaller_images == 0:

            print(f"\tDirectory {d} has {num_images} but it looks like we haven't shrunk them yet.")
            shrunk_success = shrink_wrapper(path_to_dir, num_images)

            if shrunk_success:

                remove_fullsize_images(path_to_dir, num_images)
            
            if dest:

                copy_small_images(path_to_dir, dest)

        # case 3: images have been copied and shrunk, fullsize already removed
        elif num_images == num_smaller_images:

            print(f"\tDirectory {d} image counts look good, moving on.")

            if dest:

                copy_small_images(path_to_dir, dest)


        # case 4: images have been copied and shrunk, but fullsize are still present
        elif num_images == 2 * num_smaller_images:

            print(f"\tDirectory {d} has 2x as many big images as small ones.")
            remove_fullsize_images(path_to_dir, num_images)

            if dest:

                copy_small_images(path_to_dir, dest)

        else:

            print(f"\Directory {d} has an unexpected number of images. Please go look.")

