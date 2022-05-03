# Dump dev database into a json fixture
# - used for testing
# - assumes user has a dev instance in their /apps/django user space  

set -e

FIXTURE_NAME=$1
FIXTURE_PATH="/apps/django/user/${USER}/dcdl_dev/EntryApp/fixtures/${FIXTURE_NAME}"

echo  "saving fixture at $FIXTURE_PATH... "

cd /apps/django/user/$USER/dcdl_dev/
mkdir -p EntryApp/fixtures/
python manage.py dumpdata --format json --indent 4  > $FIXTURE_PATH

set +e