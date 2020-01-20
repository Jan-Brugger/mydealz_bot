# mydealz_bot

## Getting started

### Requirements 
* python 3.7

### Installing

Configure your project virtual environment:

    python3 -m venv ./venv

Switching to your virtual environment:

    source ./venv/bin/activate
    
Installing virtual environment dependencies:

    export PYCURL_SSL_LIBRARY=openssl
    pip install -r requirements.txt
    
Creating config
    
    cp ./config/config.ini.example ./config/config.ini


### Checks Before Commit

After adding extra dependencies to project please regenerate new requirements file:

    ./venv/bin/pip freeze > requirements.txt
    
### Service lunching

To make sarver accesble with http request you should start it wit command:

    ./venv/bin/python run.py

To stop it press:

    Control + C

### Validate code syntax with pylint
    pylint ./*.py src
     