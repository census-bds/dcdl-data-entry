#!/bin/sh
APP_DIR=$1

# activate the dcdl conda environment
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl_gunicorn

# move to app dir and start django at correct port
if [ $APP_DIR = 'dcdl_test' ]
then
    cd /apps/django/dcdl_test
    # python manage.py runserver 7000
    gunicorn dcdl.wsgi 127.0.0.1:7000 -w 8 

elif [ $APP_DIR = 'dcdl_data_entry' ]
then
    cd /apps/django/dcdl_data_entry
    # python manage.py runserver 8000
    gunicorn dcdl.wsgi -w 8 



