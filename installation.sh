#!usr/bin/bash
#=======================================================================#
# STEPS FOR SETTING UP A NEW INSTANCE
# begins after you clone the repo into the directory where it will live 
#=======================================================================#

# starting in the repo root
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
for reel in "1970_Alabama_303" "1970_Michigan_151" "1970_Florida_1204" "1970_Kansas_176"; do

    mkdir /data/storage/images/training_images/1970/$reel;
    find /data/storage/images/1970/$reel/*_00[0-5][0-9].jpg -exec cp -R {} /data/storage/images/training_images/1970/$reel/ \;

done

# move ~60 images from 1980 reels
for reel in "1980_California_1032" "1980_Colorado_678" "1980_Florida_2138" "1980_Georgia_600" "1980_Texas_3951" ; do

    mkdir /data/storage/images/training_images/1980/$reel;
    find /data/storage/images/1980/$reel/*_00[0-5][0-9].jpg -exec cp -R {} /data/storage/images/training_images/1980/$reel/ \;

done

# move ~50 images from 1990 reels
for reel in "1990_11025574" "1990_41067349" "1990_56071517"; do

    mkdir /data/storage/images/training_images/1990/$reel;
    find /data/storage/images/1990/$reel/*_00[0-4][0-9].jpg -exec cp -R {} /data/storage/images/training_images/1990/$reel/ \;

done



# 2. CREATE NEW DB

source /data/data/postgresql/activate_conda_env.sh
psql postgres -c "CREATE DATABASE dcdl_train WITH OWNER django_user;"
conda deactivate


# 3. CONFIGURE SETTINGS.PY
cp dcdl/example_settings.py dcdl/settings.py
# then modify it!!! 
# - change app instance to train
# - add secret key
# - change database to dcdl_train and add django_user postgres PW
# - change MEDIA_ROOT and STATIC_ROOT

# set up logging directory
mkdir /data/data/user/django_user/train/
mkdir /data/data/user/django_user/train/logs


# 4. MIGRATE THE DB
python manage.py makemigrations
python manage.py migrate 


# 5. COLLECT STATIC IMAGES

mkdir /data/data/user/django_user/train/static/

cp -R /data/data/user/django_user/prod/static/openseadragon_images /data/data/user/django_user/train/static

python manage.py collectstatic


# 6. ADD USERS

#



# 7. LOAD FORM FIELDS

# grab form_fields.csv from prod
cp ../dcdl_data_entry/form_fields.csv .



# 8. LOAD IMAGES