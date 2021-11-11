#!usr/bin/bash
#=======================================================================#
# STEPS FOR SETTING UP A NEW INSTANCE
# begins after you clone the repo into the directory where it will live 
#=======================================================================#

cd /apps/django/training/

# 1. COLLECT IMAGES INTO RELEVANT DIRECTORY

# first make directories
mkdir /data/storage/images/training_images

for year in "1960" "1970" "1980" "1990"; do 

    mkdir /data/storage/images/training_images/$year;

done

# move training reel from 1970
cp -R /data/storage/images/1970/1970_Illinois_391 /data/storage/images/training_images/1970/

# move ~60 images from other 1970 reels
for reel in "1970_Alabama_303" "1970_California_3301" "1970_Florida_1204" "1970_Kansas_176"; do

    mkdir /data/storage/images/training_images/1970/$reel;
    find /data/storage/images/1970/$reel/*_00[0-5][0-9].jpg -exec cp -R {} /data/storage/images/training_images/1970/$reel/ \;

done

# move ~60 images from 1980 reels
for reel in "1980_California_1032" "1980_Colorado_678" "1980_Florida_2138" "1980_Georgia_600" "1980_Texas_3951" ; do

    mkdir /data/storage/images/training_images/1980/$reel;
    find /data/storage/images/1980/$reel/*_00[0-5][0-9].jpg -exec cp -R {} /data/storage/images/training_images/1980/$reel/ \;

done


# 2. CREATE NEW DB

source /data/data/postgresql/activate_conda_env.sh
psql postgres -c "CREATE DATABASE dcdl_train WITH OWNER django_user;"
conda deactivate

# 3. CONFIGURE SETTINGS.PY
cp ../dcdl_data_entry/dcdl/settings.py dcdl/example_settings.py 
# then modify it!!! 
# - change app instance to train
# - change database to dcdl_train
# - change MEDIA_ROOT and STATIC_ROOT

# logging directory
mkdir /data/data/user/django_user/train/
mkdir /data/data/user/django_user/train/logs

