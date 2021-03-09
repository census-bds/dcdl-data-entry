#!usr/bin/bash

# user needs to ssh into the server

# run new_aws_user setup script
cd /data/data/git/cloud_tools/aws_bash
source new_aws_user.sh

# there are some prompts that may pop up - how do I get them to say yes automatically?

# activate conda and create a new environment
source /apps/user/${USER}/miniconda3/bin/activate

if [${USER}='genad001']
then
    conda remove -p /apps/user/${USER}/conda_envs/dcdl --all 
    conda remove -p /apps/user/${USER}/conda_envs/dcdl2 --all
fi 

conda create -p /apps/user/${USER}/conda_envs/dcdl python=3.8.5
conda activate /apps/user/${USER}/conda_envs/dcdl

# install required packages: better to do this from requirements.txt
pip install django
pip install django-crispy-forms
pip install django-queryset-csv
