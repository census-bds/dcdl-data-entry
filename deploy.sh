### Deploy a change (assumes PR request is closed)
set -e 

VERSION_NO=$1

cd /apps/django/dcdl_data_entry
source /apps/user/$USER/miniconda3/bin/activate /apps/user/$USER/conda_envs/dcdl

# do git fetch and merge in gitlab (via PR)
git pull origin master
git tag $VERSION_NO
git push origin tag

# TODO:
# script can ensure that the tag is applied
# automatically increment version number by 1 (find bash code for this)
# git tag runs against a commit (whatever one is checked out)

# run tests again here
python manage.py test EntryApp.tests.test_views

# reload application
touch dcdl/wsgi.py

# TODO: check if prod is running 
# endpoint on the application that gets the latest git tag and renders it
# curl localhost:8000 and ensure we get tag number we're expecting
# do this with a view that doesn't require authentication

