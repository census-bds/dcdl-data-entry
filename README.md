## Decennial Census Digitization and Linkage (DCDL) - Data Entry Application

The Decennial  Census Digitization  and Linkage  project  (DCDL) is an initiative  to  produce  linked restricted  microdata  files  from  the decennial  censuses of 1960  through  1990. This tool enables hand-entry of data from a subset of scanned images of the historical files, an essential part of developing a scalable tool to capture respondent information so that individuals can be studied over time.

If you have access to GitLab, please see the project wiki. The instructions below are intended for the public GitHub.

## Instructions for setting up the app on a new server

Before you begin, ensure that you have Python >3.8 and Postgresql installed. If you are using the default BDS setup, make sure you've run the cloud_tools new AWS user setup and Postgres install scripts.

1. Clone the repository.

2. Create a virtual environment (conda or pip) and install the required packages in requirements.txt. Activate the environment.

3. If using Postgresql, ensure Postgres is running and create a database for the Django project. You must be a Postgres superuser in order to do this.

    - On a CSVD GovCloud server using the BDS default setup, check if Postgres is running:
    
    ```
    cd /data/data/postgresql
    source /apps/user${USER}/miniconda3/bin/activate /data/data/postgresql/conda_env
    psql postgres # if this prompts you for a password, postgres is running
    
    # if Postgres is not running, start it and enter shell 
    source start_postgresql.sh    
    psql postgres

    # check which users exist
    \du
    
    # create django user if needed
    CREATE ROLE django_user WITH LOGIN;
    ALTER ROLE django_user WITH PASSWORD '<password>'; 

    # in order to enable automated testing, allow django_user to create databases
    ALTER ROLE django_user CREATEDB;
    ```

    - Create a database. The default configuration for this Django project is to have a dev database named dcdl_dev, a test database named dcdl_test, and a production database named dcdl_prod, and to have a user-owner for all three named django_user.

   ```
   CREATE DATABASE <db_name> WITH OWNER django_user; 
   ```

4. Copy `dcdl/example_settings.py` into a new file called `dcdl/settings.py`. Then configure the copy (i.e. `dcdl/settings.py`, which is .gitignored). Currently, the example settings assume a Postgres backend, so you need to enter the Django secret key and the password for django_user and confirm that the database name is correct (i.e. dcdl_dev for a dev version, dcdl_test for a test version, and dcdl_prod for production).

5. Make migrations and apply them. If you're re-creating the database for dev or test purposes and you run into problems, you may need to delete and re-create them. You may not want to check them into git until you're moving towards production, as merge and migration conflicts can get tricky.

     ```
     python manage.py makemigrations
     python manage.py migrate
     ```

6. Create an admin: `python manage.py createsuperuser`. You will be prompted for an admin username, email, and password.

7. Collect static images for the image viewer tool's navigation buttons. 

    - The static files live in '/data/data/user/django_user/<APP INSTANCE>/static/openseadragon_images', where APP INSTANCE can be one of dev, test, or prod. Check that this path is listed in `STATICFILES_DIRS` in `settings.py`. 
    - While you're looking at `settings.py`, check that `STATIC_ROOT` is set to `os.path.join(BASE_DIR, 'static/')`. This configuration means django will collect static files into a subdirectory called `static/` at the same level as `manage.py`.
    - Run `python manage.py collectstatic` and say yes when asked if you want to continue. This will create the `static/` subdirectory and copy the static files into it. Other static files will come in for the admin and for the EntryApp specific css.

Next steps: create data entry user group and user accounts. See How to create users.

### How to create users

The initial setup has three components: creating users, assigning images to those users, and loading the specified fields for each form. Image assignment has to happen after users are created, but loading form fields doesn't depend on either of the other two.

1. Add a data entry group and create users assigned to that group. First, add user data to `user_info.csv`. Use the methods in `EntryApp/create_users.py` to create a data entry group, create individual users using the credentials in the csv file, and to add the users to the data entry group.

    ```
    # default usage
    python manage.py shell

    # at shell prompt
    import EntryApp.create_users as users
    users.create_entry_group()
    users.bulk_load_entry_users() # option to use a different string filepath to a user csv file here if needed

    # if a custom user add is needed, use this method rather than bulk load to ensure no existing data is overwritten  
    users.add_entry_user(<username>, <password>)
    ```

2. Add form fields, again using the methods in `EntryApp/load_db.py`.   
- This module assumes you have the form fields saved in a csv file in the base directory (same level as manage.py), where the first three columns are respectively the year, the form type, and the field name. Change the global variable in `EntryApp/load_db.py` to change this.

    ```
    $ python manage.py shell
  
    # in the shell. customize args if needed
    from django.conf import settings
    import EntryApp.load_db as ldb
    ldb.load_form_fields(settings.FORM_FIELDS_CSV) # populate FormField model
    ```

3. Create dummy breakers

Since 1990 does not have breakers, we create a dummy reel with a dummy breaker for each user to satisfy the DB integrity constraint so we can use the same data model across years. We only need to take this step one time per user: it should happen the first time that images are loaded, and then any time a new user is added. Note that the dummy reel created with this method assigns the reel to 'jbid123' (hard-coded) for both keyer slots, so it's going to look weird. 

Here's how to create dummy breakers:

```
    $python manage.py shell

    # in the shell. customize args if needed
    from django.conf import settings
    import EntryApp.load_db as ldb

    # do this once
    ldb.create_1990_dummy_breakers([]) # create one dummy breaker for 1990 for all known keyers
``` 

4. Upload reels of images to the database using the methods in `EntryApp/load_db.py`. See instructions below on provisioning images and loading them into the database. 


#### Adding users after the initial load

1. Use the `add_entry_user()` method to ensure that data for existing users is not overwritten.

```
    # if a custom user add is needed, use this method rather than bulk load to ensure no existing data is overwritten  
    users.add_entry_user(<username>, <password>)
```

2. Then add a dummy breaker image for this new user.

```
    $python manage.py shell

    from django.conf import settings
    import EntryApp.load_db as ldb

    # do this if there is a new keyer added
    ldb.create_1990_dummy_breakers(['new_username'])

```

### Provisioning images

The application expects to serve images from a nested directory structure within a path specified as the `MEDIA_ROOT` in `settings.py`. You will need to move the images you want to key onto your machine and set up that directory structure. Images are scanned in reels, so each reel contains images from the same year in a geographic area. The app expects files to be stored based on this structure.  For example:

```
/path/to/images/
-1960
    \_reel1_1960
    \_reel2_1960
-1970
    \_reel1_1970
    \_reel2_1970
-1980
    \_reel1_1980
    \_reel2_1980
-1990
    \_reel1_1990
    \_reel2_1990
```


### How to load images into the database

Loading a reel populates the Reel model as well as the ImageFile model. Initially, reels are not assigned to keyers, and the Image model does not get populated until a reel is assigned. Please refer to the section on reel assignment for instructions on how to assign a reel to a specific keyer.

#### Load reels from a csv file 

The csv should have a header row and each subsequent row should be of the form ```filepath, year, state```. Example

```
file_path,year
/data/data/images/dev_images/1960/dev_1960,1960,IL
/data/data/images/dev_images/1970/dev_1970,1970,AL
```
To load this, use methods in ```load_db.py```.

```
$ python manage.py shell

# in the shell
import EntryApp.load_db as ldb
ldb.load_reels_from_csv('<path to csv>')
```

#### Load a single reel from the shell

```
$ python manage.py shell

# in the shell
import EntryApp.load_db as ldb
ldb.load_reel('/data/data/images/dev_images/1960/dev_1960', 1960, 'IL')
```

### Start the app

### For dev

1. Activate the `dcdl` conda environment for your user (you need to create this on first setup).

2. Navigate to one of the following directories:
    - Production: `/apps/django/dcdl_data_entry`
    - Test: `/apps/django/dcdl_test`
    - Dev: `/apps/django/$USER/dcdl_dev`

3. Run one of the following commands to start the app:

```
# default setting: run app in terminal at port 8000
python manage.py runserver

# run at different port, e.g. 7000 for test and 8001 for dev
python manage.py runserver 7000

# run at port 7000 using screen, session name
screen -dmS <screen session name> python manage.py runserver 7000
```

4. Set up port forwarding, e.g. with `ssh -L 8000:localhost:8000 <username>@my-server@host.domain`.

#### Cron jobs (for production) 

Run `crontab -e` to review and/or edit the cron instructions.

Currently, the crontab does the following:
- starts the postgres instance
- activates the user's DCDL conda environment
- starts the test version of the app at port 7000
- starts the prod version of the app at port 8000

The contents of the crontab are:
```
SHELL=/bin/bash
HOME=/
EMAIL=""
# Start postgres and start the test app when the server boots
@reboot /data/data/postgresql/start_pgsql.sh >> /data/data/postgresql/cronlog.out 2>&1
@reboot /apps/django/dcdl_test/start_app.sh >> /data/data/user/django_user/test/logs/cronlog.out 2>&1
@reboot /apps/django/dcdl_data_entry/start_app.sh >> /data/data/user/django_user/prod/logs/cronlog.out 2>&1
```


## Other documentation

### Access backend databases

The production server is configured with three databases, one each for development, testing, and production. The dev database is called dcdl_dev, the test database is called dcdl_test, and the prod database is called dcdl_data_entry. There is a generic user named django_user who is an owner for each.

1. Activate the postgres conda environment by running source /data/data/postgresql/activate_conda_env.sh.

2. Access the dev, test, or prod DB with the following command: psql <dbname> -U django_user

3. Enter the password for django_user.

### Backend DBs

All backend DBs are owned by a generic user called `django_user`. All passwords are stored in a separate, password-protected location on a network drive.

Each version of the entry application - dev, test, and prod - has its own backend database and lives in a different area of the server. 

Each version has its own `settings.py` module. This module contains the configuration for the app, including the backend DB, the paths for images and static files, and the logging specs. It is not checked into git, so merging branches should not affect this file. There is an `example_settings.py` file that is checked into git that contains all configuration information except the secret key and DB login info.

#### Production app

- the application lives in `/apps/django/dcdl_data_entry`
- the Postgres for production is called `dcdl_prod`
- the git branch for production is master
- images for production are currently saved in `/data/data/images`, with subdirectories for each reel within each year
     - `MEDIA_ROOT` and `IMAGE_DIR` should be `/data/data/images/` 
- the cron job should run this version on port 8000

#### Test app

- the application lives in `/apps/django/dcdl_test`
- the Postgres for production is called `dcdl_test`
- the git branch for production is test
- images for testing are currently saved in `/data/data/images/test_images` with subdirectories for an example reel within each year
     - `MEDIA_ROOT` and `IMAGE_DIR` should be `/data/data/images/test_images` 
- the cron job runs this version on port 7000


#### Dev app

- the application lives in the user's space in `/apps/django/user/$USER/dcdl_dev`
- the Postgres for production is called `dcdl_dev`
- the git branch for production is dev
- images for dev are puppies and nature and are currently saved in `/data/data/images/dev_images` 
     - `MEDIA_ROOT` and `IMAGE_DIR` should be `/data/data/images/dev_images` 
in subdirectories for reels within each year
- it should run on port 8001

### Backups

The module `manage_backups.py` essentially wraps the Postgres `pg_dump` command to enable scheduled backups (via cron) as well as manual backups. 

To run a backup manually, run `python manage_backups.py run_backup`.

For scheduling backups with cron, use the `run_backup.sh` shell script with the top-level directory as an argument.

### Deploy changes from dev to test and prod

The flow for this project has been `dev -> test -> prod`. Changes to dev happen on the dev branch in the user's dev version of the app, are merged into test in the test version of the app (`/apps/django/dcdl_test`), and finally get merged into master in the prod version of the app (`/apps/django/dcdl_data_entry`).

##### Steps for merging dev into test

- Commit and push the most recent changes from dev to the dev branch. 
- CD to the test area and run `git fetch` to sync those commits locally.
- Make sure you're on the test branch. Run `git merge origin dev` and resolve any conflicts.
- Commit and push to the test branch.
- You will need to manually make any changes to `settings.py` because it is not checked into git. One way to keep track of changes is to make corresponding changes in `example_settings.py`, which is checked in, but ultimately you will still need to ensure those changes make it into the `settings.py` file.
- Make any necessary updates to the backend databases. 

##### Steps for merging test into master

- Commit and push the most recent changes from test to the test branch. 
- CD to the prod area and run `git fetch` to sync those commits locally.
- Make sure you're on the master branch. Run `git merge origin test` and resolve any conflicts.
- Commit and push to the master branch.
- You will need to manually make any changes to `settings.py` because it is not checked into git. One way to keep track of changes is to make corresponding changes in `example_settings.py`, which is checked in, but ultimately you will still need to ensure those changes make it into the `settings.py` file.
- Make any necessary updates to the backend databases.

### Reel assignment

The default model assigns reels to keyers as keyers complete reels. It is possible to assign specific reels to specific keyers through the shell. 

#### Default approach to reel assignment

Each time a keyer logs into the application, the app will check to see if they have a reel assigned in the `CurrentEntry` model. 

If no row exists for that keyer, the application will create one. This process occurs in the `assign_reel` method` in `views.py`. It queries the Reel model and returns a queryset of reels in the following order:
- filters for reels where the `keyer_count` is less than 2
- excludes the dummy breaker reel
- excludes reels that have already been assigned to this keyer 
- orders the reels in ascending order by keyer count, so that reels with no keyers assigned already are preferred to reels with one keyers assigned
- orders reels in ascending order by the auto-generated ID, so that reels loaded earlier are preferred to reels loaded later

This method will assign the keyer to the `keyer_one` slot if available, and the `keyer_two` slot if not, and it will increment the keyer count. It also increments the `reel_count` attribute in the Keyer model.

Next, the `assign_reel_to_keyer()` method from `EntryApp.load_db` will create an Image instance for each ImageFile in the reel for the keyer. If a keyer has a reel assigned already, this method will not affect that; it will simply ensure that the next reel in the queue for that keyer is the specified one. 

#### What happens when a keyer is done with a reel?

When a keyer has moved through all of the images in a reel, a button labeled "Load next reel" will appear near the top of the page on the home screen. When the keyer clicks this button, the page will reload. If there is a new reel, the keyer will see those images for entry. If no reels are available, the page will stay on the last reel.

This logic is controlled by the `get_next_reel()` method in `views.py`.

#### How to assign a specific reel to a specific keyer

If you need to assign a specific reel to a specific keyer, you can do that using the `assign_reel_to_keyer()` method in the shell. In the snippets section of this repo, there is also a snippet with code that assigns a list of reels to a list of keyers.

```
$ python manage.py shell

# in the shell
import EntryApp.load_db as ldb
from EntryApp.models import Reel, Keyer

# get specified reel and keyer instances
this_reel = Reel.objects.get(reel_name='your_reel_name')
this_keyer = Keyer.objects.get(jbid='keyer_jbid')

# check which keyer positions are open
this_reel.keyer_one
this_reel.keyer_two

# do assignment to position 1
ldb.assign_reel_to_keyer(this_reel, this_keyer, 1)
```

### Update record fields

Updating the fields entered for each person record (i.e. each entry in Record) requires making changes in several areas of the app. This page describes each.

1. Update the Record model in models.py and run a migration. This is only necessary if the name of a field captured in a record changes: for example, changing `firstname` to `first_name`.

2. Update the FormField csv file to reflect the new names. The values in the field names column must match the names of fields in the Record model. 

3. Update the form layout in layouts.py to ensure that the updated fields appear as desired.

4. (May not be necessary for all fields) Update the widget dictionary in RecordForm in forms.py. This might not be necessary if the new/updated field widgets are the default widgets for that type of ModelField.