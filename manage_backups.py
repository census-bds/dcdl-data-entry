import argparse
from contextlib import contextmanager
import os
import pathlib
import sys

import subprocess
from datetime import datetime

import dcdl.settings as settings

"""
Backup management script. Works off of django settings file
to create/restore backups of the default database specified in settings.py
"""

OUTPUT_BASE="/data/holder/backup"

# by default, pgpass file gets created in cwd
# (in case of this script, project root)
PGPASS_PATH = os.path.join(pathlib.Path().resolve(), ".pgpass")

@contextmanager
def pgpass_context(db_settings):
    """
    In order to supply password, postgres requires a ~/.pgpass file.
    https://stackoverflow.com/questions/2893954/how-to-pass-in-password-to-pg-dump

    This context manager creates that file and then deletes when script ends
    (or dies).

    Note: if you have a ~/.pgpass file, this script will die and warn you.

    """

    if os.path.exists(PGPASS_PATH):
        raise KeyError("the .pgpass file exists, move before running this.")

    pgpass_str = "{host}:{port}:*:{user}:{password}\n"\
        .format(host=db_settings["HOST"],
                port=db_settings["PORT"],
                user=db_settings["USER"],
                password=db_settings["PASSWORD"])

    with open(PGPASS_PATH, "w+") as pgpass_f:
        pgpass_f.write(pgpass_str)

    os.chmod(PGPASS_PATH, 0o600)

    try:
        yield
    finally:
        os.remove(PGPASS_PATH)


def _gen_output_path(db_settings):
    """
    Helper function to generate output file for this backup.
    """

    timestr = datetime.now().strftime("%Y_%m_%d__%H%M")

    fname = "{name}_{time}.sql".format(name=db_settings["NAME"],
                                       time=timestr)
    out_path = os.path.join(OUTPUT_BASE, fname)
    return out_path


def run_backup(db_settings):
    """
    Backs up database specified in django config.

    Uses pg_dump command. All pg_dump stderr messages are printed to terminal.
    """
    command = "pg_dump -U {} -d {}".format(db_settings["USER"], db_settings["NAME"])
    out_path = _gen_output_path(db_settings)

    env = os.environ.copy()
    env["PGPASSFILE"] = PGPASS_PATH

    with open(out_path, "w+") as out_f:
        subprocess.run(command, shell=True, stdout=out_f, env=env)


def restore_backup(backup_path, db_settings, new_db_name):
    """
    Restores backup from specified file to a new database.
    Uses the user / account info from django config.

    To restore an app to a backup version, steps would be:
       1. Get path of latest backup.
       2. Restore backup to new database.
       3. Point production to new database.
    """

    # db is because otherwise the .pgpass file doesnt work
    create_command = "psql -d {db} -U {user} -c 'CREATE DATABASE {name} WITH OWNER {user};'"\
                         .format(db=db_settings["NAME"], user=db_settings["USER"], name=new_db_name)
    restore_command = "psql -U {user} -d {new_db_name} -f {backup_path}"\
                         .format(user=db_settings["USER"],
                                 new_db_name=new_db_name,
                                 backup_path=backup_path)
    env = os.environ.copy()
    env["PGPASSFILE"] = PGPASS_PATH
    res = subprocess.run(create_command, shell=True, env=env)
    if res.returncode != 0:
        print("Error with DB creation command. The database may exist. Check command line output for messages from psql.")
        sys.exit(1)

    subprocess.run(restore_command, shell=True, env=env)


commands = ["run_backup", "restore_backup"]
command_helptext = 'Which command to run. Options: {}'.format(", ".join(commands))
new_db_helptext = 'Name of new database. Required if running restore_backup'
backup_path_helptext = 'Location of backup file. Should be a .sql file. Required if running restore_backup'
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Do backup stuff.')
    parser.add_argument('command', help=command_helptext, choices=commands)
    parser.add_argument('backup_path', nargs="?", help=backup_path_helptext)
    parser.add_argument('new_db_name', nargs="?", help=new_db_helptext)
    args = parser.parse_args()

    db_settings = settings.DATABASES['default']
    with pgpass_context(db_settings):
        if args.command == 'run_backup':
            run_backup(db_settings)
        elif args.command == 'restore_backup':
            if args.new_db_name is None or args.backup_path is None:
                parser.error("new_db_name and backup_path required to restore backup")
            restore_backup(args.backup_path, db_settings, args.new_db_name)
