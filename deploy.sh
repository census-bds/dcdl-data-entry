### Deploy a change from dev to prod

## DEV: RUN AUTOMATED RESTS

# make sure we're in the right place and that conda is activated
cd /apps/django/${USER}/dcdl_dev/
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl

# run tests
python manage.py tests EntryApp.tests.test_views

# TODO: how do we tell if we pass?

## PASSED TESTS: MOVE TO PROD

cd /apps/django/dcdl_data_entry

git fetch
git checkout dev
git pull origin dev
git checkout master
git merge dev

# run tests again here
python manage.py tests EntryApp.tests.test_views
# TODO: do we pass? 

# reload application
touch dcdl/wsgi.py

# TODO: check if prod is running 
