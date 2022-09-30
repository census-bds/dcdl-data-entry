#!/bin/bash
# Dump dev database into a json fixture
# - used for testing
# - assumes user has a dev instance in their /apps/django user space  
# - excludes the Django ContentTypes model because it has caused errors

set -e

FIXTURE_NAME=$1
FIXTURE_PATH="/apps/django/user/${USER}/dcdl_dev/fixtures/${FIXTURE_NAME}"

echo  "saving fixture at $FIXTURE_PATH... "

cd /apps/django/user/$USER/dcdl_dev/
mkdir -p fixtures/
python manage.py dumpdata --format json --indent 4 --exclude contenttypes  > $FIXTURE_PATH

set +e