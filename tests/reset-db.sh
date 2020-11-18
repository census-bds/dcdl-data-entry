#!/usr/bin/bash
echo "Nuking your database..."
rm EntryApp/migrations/0*.py
rm EntryApp/migrations/__pycache__/0*.pyc 
rm db.sqlite3

echo "migrations folder contents:"
ls -lh EntryApp/migrations

echo "the db file should also be gone:"
ls