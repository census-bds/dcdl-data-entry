import argparse
from contextlib import contextmanager
import os
import pathlib

import subprocess
import time

import dcdl.settings as settings

"""
Backup management script. Works off of django settings file
to create/restore backups of the default database specified in settings.py
"""

OUTPUT_BASE="/data/data/backup"

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

    pgpass_str = "{host}:{port}:{name}:{user}:{password}\n"\
        .format(user=db_settings["USER"],
                password=db_settings["PASSWORD"],
                host=db_settings["HOST"],
                port=db_settings["PORT"],
                name=db_settings["NAME"])

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

    fname = "{name}_{time}.sql".format(name=db_settings["NAME"],
                                       time=int(time.time()))
    out_path = os.path.join(OUTPUT_BASE, fname)
    return out_path


def run_backup(db_settings):
    """
    Backs up database specified in django config.

    Uses pg_dump command. All pg_dump stderr messages are printed to terminal.
    """
    command = "pg_dump {}".format(db_settings["NAME"])
    out_path = _gen_output_path(db_settings)

    env = os.environ.copy()
    env["PGPASSFILE"] = PGPASS_PATH

    with open(out_path, "w+") as out_f:
        subprocess.run(command, shell=True, stdout=out_f, env=env)


def restore_backup(backup_path, new_db_name):
    """
    Restores backup from specified file to a new database.
    Uses the user / account info from django config.

    To restore an app to a backup version, steps would be:
       1. Get path of latest backup.
       2. Restore backup to new database.
       3. Point production to new database.
    """
    pass


commands = ["run_backup", "restore_backup"]
helptext = 'Which command to run. Options: {}'.format(", ".join(commands))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Do backup stuff.')
    parser.add_argument('command', help=helptext, choices=commands)
    args = parser.parse_args()

    db_settings = settings.DATABASES['default']
    with pgpass_context(db_settings):
        if args.command == 'run_backup':
            run_backup(db_settings)
        elif args.command == 'restore_backup':
            restore_backup()
