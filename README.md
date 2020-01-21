# mydealz_bot

## Getting started

### Requirements 
* Python 3.7
* Docker

### Installing

Configure your project virtual environment:

    python3 -m venv ./venv

Switch to your virtual environment:

    source ./venv/bin/activate
    
Install virtual environment dependencies:

    export PYCURL_SSL_LIBRARY=openssl
    pip install -r requirements.txt
    
Create config
    
    cp ./config/config.ini.example ./config/config.ini
    
Install pre-commit hooks

    pre-commit install


### Checks Before Commit

After adding extra dependencies to project please regenerate new requirements file:

    ./venv/bin/pip freeze > requirements.txt
    
### Service lunching

Run service in Python:

    ./venv/bin/python run.py

To stop it press:

    Control + C
    
Create Docker container:

    docker build -t mydealz_bot .

Run Docker container:
    
    docker run --name mydealz_bot mydealz_bot
    
Run Docker container in background:

    docker run -dit --restart unless-stopped --name mydealz_bot mydealz_bot
    
Stop Docker container:
    
    docker stop mydealz_bot

### Validate code syntax with pylint
    pylint ./*.py src
     