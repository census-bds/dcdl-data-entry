find . -path "EntryApp/migrations/*.py" -not -name "__init__.py" -delete
find . -path "EntryApp/migrations/*.pyc" -delete

rm db.sqlite3