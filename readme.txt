Requirement python 3.8 or later

1- Install virtualenv in you python environment
    pip install virtualenv
2- create a new virtual environment
    virtualenv bwlenv
3- start your virtualenv
    path-to-your-virtualenv-folder/bwlenv/Script activate (on windows)
    sh path-to-your-virtualenv-folder/bwlenv/bin activate (on linux)
4 Install your requirement files package
    pip install -r path-to-your-project-folder (bwl_backend)/scripts/requirements.txt
3 start django 
    python manage.py runserver 80
6- type localhost/admin in your browser and enjoy