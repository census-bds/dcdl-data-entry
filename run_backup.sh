#!/bin/bash

echo "==========================="
echo "Running backup... on `date`"
source /apps/user/${USER}/miniconda3/bin/activate /apps/user/${USER}/conda_envs/dcdl
python manage_backups.py run_backup
echo "====== Done. Any error / logs above. ============"
