#!/bin/sh

# activate the dcdl conda environment
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl

# move to app dir and start django at 7000
cd /apps/django/dcdl_test
python manage.py runserver 7000