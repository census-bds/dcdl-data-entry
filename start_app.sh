#!/bin/sh
set -e
APP_DIR=$1

# activate the dcdl conda environment
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl

# move to app dir and start django at correct port
if [ $APP_DIR = 'dcdl_data_entry' ]
then
    cd /apps/django/dcdl_data_entry
    python manage.py runmodwsgi --port 8000 --server-root=/tmp/httpd_production --url-alias /images /data/storage/images --document-root /data/storage/images


elif [ $APP_DIR = 'dcdl_train' ]
then
    cd /apps/django/dcdl_train
    python manage.py runmodwsgi --port 7000 --server-root=/tmp/httpd_training --url-alias /images /data/storage/images/training_images --document-root /data/storage/images/training_images

elif [ $APP_DIR = 'dcdl_test' ]
then
    cd /apps/django/dcdl_test
    python manage.py runmodwsgi --port 7002  --document-root /data/storage/images/test_images/ --server-root=/tmp/httpd_test --url-alias /images /data/storage/images/test_images

fi


