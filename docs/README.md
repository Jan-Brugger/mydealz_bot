# mydealz_bot

### Requirements

* Python 3.9.7
* Docker

### Installing

Configure your project virtual environment:

    python3 -m venv ./venv

Switch to your virtual environment:

    source ./venv/bin/activate

Install virtual environment dependencies:

    pip install --upgrade pip
    pip install -r requirements-dev.txt

Create config

    cp .env.example .env

Install pre-commit hooks

    pre-commit install

### Service launching

Run service in Python:

    python daemon.py

Run bot only:

    python src/bot.py

Run feed-parser only:

    python src/feed.py

To stop it press:

    Control + C

Build image with docker build:

    docker build -t mydealz_bot .

Build multi-platform-images with buildx:

    docker buildx build -t mydealz_bot --platform linux/amd64,linux/arm64,linux/arm/v7 .

Run Docker container:

    docker run --env BOT_TOKEN=<<YOUR_BOT_TOKEN>> --name mydealz_bot mydealz_bot

Run Docker container in background:

    docker run --env BOT_TOKEN=<<YOUR_BOT_TOKEN>> -dit --restart unless-stopped --name mydealz_bot mydealz_bot

Stop Docker container:

    docker stop mydealz_bot

Delete Docker container:

    docker rm mydealz_bot

### Validate code syntax with pylint

    pylint ./*.py src

### Validate static typing

    mypy daemon.py
