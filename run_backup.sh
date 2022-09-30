#!/bin/bash

APP_DIR=$1

echo "==========================="
echo "Running backup... on `date`"
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl
cd $APP_DIR
python manage_backups.py run_backup
echo "====== Done. Any error / logs above. ============"
