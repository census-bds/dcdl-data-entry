#!/usr/bin/bash
echo "Are you sure you want to nuke your database?"
select yn in "Y" "N"; do
    case $yn in
        Y ) rm "EntryApp/migrations/0*.py";  rm "EntryApp/migrations/0*.pyc"; rm db.sqlite3; break;;
        N ) exit;;
    esac
done