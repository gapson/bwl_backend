# bwl_backend
The Initial commit does not have any database config. We will be using sqlite3 as DB for now.

Intallation.

Requirement python 3.8 or later with pip3.8 as default pip.

1- Install virtualenv in you python environment
    pip install virtualenv
2- create a new virtual environment
    virtualenv bwlenv
    on Linux or mac add the path to python
    virtualenv -p <path to python version> venvName
3- start your virtualenv
    path-to-your-virtualenv-folder/bwlenv/Script activate (on windows)
    sh path-to-your-virtualenv-folder/bwlenv/bin activate (on linux)
    source path-to-your-virtualenv-folder/bwlenv/bin/activate (On Mac)
4 Install your requirement files package
    pip install -r path-to-your-project-folder (bwl_backend)/scripts/requirements.txt
5- Generate migration page for flatpages
    python manage.py makemigrations flatpages
6 Udate Databse
    python manage.py migrate
7 Create a super user
    python manage.py createsuperuser
7 start django 
    python manage.py runserver 80
8- type localhost/admin in your browser and enjoy
9- use endpoint /api/v1/doc/ or /api/v1/docs/ to read API documentation 

