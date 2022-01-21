#!/bin/sh
APP_DIR=$1

# activate the dcdl conda environment
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl

# move to app dir and start django at correct port
if [ $APP_DIR = 'dcdl_test' ]
then
    cd /apps/django/dcdl_test
    python manage.py runmodwsgi --port 7001

elif [ $APP_DIR = 'dcdl_train' ]
then
    cd /apps/django/training
    python manage.py runmodwsgi --port 7000

elif [ $APP_DIR = 'dcdl_data_entry' ]
then
    cd /apps/django/dcdl_data_entry
    python manage.py runmodwsgi --port 8000

fi


