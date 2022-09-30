#!/usr/bin/bash

APP_INSTANCE=$1

[[ -z `find /data/data/user/django_user/${APP_INSTANCE}/logs/error.log -mmin -10` ]]

if [ $? -eq 0 ]
then
    echo -e "nothing has changed"
else
    echo "change to ${APP_INSTANCE} error log file" | mail -s "DCDL error in ${APP_INSTANCE}" cecile.m.murray@census.gov
fi
