import os

from EntryApp.models import ImageFile, Image

# declare variables
image_qs = None
image_instance = None
image_path = None
unique_file_path_set = None
unique_file_path_list = None
file_path = None
path_head = None
path_tail = None
file_name = None
file_folder_path = None
file_counter = None
file_reel = None
image_file_qs = None
image_file_count = -1
image_file_instance = None

# get all file paths.
unique_file_path_set = set()
image_qs = Image.objects.all()
for image_instance in image_qs:

    # get image path.
    image_path = image_instance.img_path

    # is it already in set?
    if ( image_path not in unique_file_path_set ):

        # add it.
        unique_file_path_set.add( image_path )

    #-- END check to see if image path is in set. --#

#-- END loop over images --#

# make list of unique paths.
unique_file_path_list = list( unique_file_path_set )
unique_file_path_list.sort()

# what have we got?
file_reel = "test_reel"
file_counter = 0
for file_path in unique_file_path_list:

    # increment counter
    file_counter += 1

    # get folder path and file name from path.
    path_head, path_tail = os.path.split( file_path )
    print( "- file_path: {head} / {tail}".format( head = path_head, tail = path_tail ) )

    # create ImageFile
    # Does ImageFile for this path already exist?
    image_file_qs = ImageFile.objects.filter( img_path = file_path )
    image_file_count = image_file_qs.count()
    if ( image_file_count == 0 ):

        # make new.
        image_file_instance = ImageFile()

    elif ( image_file_count == 1 ):

        # load existing
        image_file_instance = image_file_qs.get()

    else:

        # more than 1? Oh dear...
        print( "ERROR - more than one ImageFile for path {image_path} - punting for now.".format( image_path = file_path ) )
        image_file_instance = None

    #-- END check to see if we already have instance for this file path. --#

    # got an instance?
    if ( image_file_instance is not None ):

        # update with values.
        image_file_instance.set_image_path( file_path )
        image_file_instance.img_reel = file_reel
        image_file_instance.img_position = file_counter
        image_file_instance.save()

        print( "----> ImageFile: {image_file}".format( image_file = image_file_instance ) )

        # store ImageFile ForeignKey in matching Image rows.

        # find all Image() instances with this image path.
        image_qs = Image.objects.filter( img_path = file_path )

        # for each, add foreign key to this image file and save.
        for image_instance in image_qs:

            image_instance.image_file = image_file_instance
            image_instance.save()

            print( "--------> Added to Image: {image}".format( image = image_instance ) )

        #-- END loop to add image to

    #-- END check to see if we have an image instance to work with. --#

#-- END loop over file paths. --#
