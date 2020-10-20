#!/usr/bin/bash
echo "Are you sure you want to nuke your database?"
select yn in "Y" "N"; do
    case $yn in
        Y ) rm EntryApp/migrations/0*.py;  rm EntryApp/migrations/__pycache__/0*.pyc; rm db.sqlite3; exit;;
        N ) exit;;
    esac
done