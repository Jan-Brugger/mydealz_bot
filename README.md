# mydealz_bot docker image
This is a Docker container to run an telegram bot, to track mydealz.de for new deals.

Currently only armv7 is supported.

### Usage

#### Command line

    docker run -d --name=mydealz_bot \
    --restart=always \
    -v /opt/mydealz_bot/files:/usr/src/app/files \
    --env BOT_TOKEN=<<YOUR_BOT_TOKEN>> \
    weltraumpenner/mydealz_bot:latest

#### Command line Options

| Parameter                                    | Description                                                                                                               |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| --restart=always                             | Start the container when Docker starts (i.e. on boot/reboot).                                                             |
| -v /opt/mydealz_bot/files:/usr/src/app/files | Mount directory /usr/src/app/files from host machine. This directory contains the database, persistent chat-data and logs |
| --env BOT_TOKEN=<<YOUR_BOT_TOKEN>>           | Your telegram-bot token. You can create one with @BotFather                                                               |

#### docker-compose

    version: '3'
    services:
      mydealz:
        container_name: mydealz
        image: weltraumpenner/mydealz_bot:latest
        restart: always
        volumes:
          - /opt/mydealz_bot/files:/usr/src/app/files
        environment:
          - BOT_TOKEN=<<YOUR_BOT_TOKEN>>

### Development

#### Requirements
* Python 3.7
* Docker

#### Installing

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


#### Checks Before Commit

After adding extra dependencies to project please regenerate new requirements file:

    ./venv/bin/pip freeze > requirements.txt

#### Service launching

Run service in Python:

    python daemon.py

Run bot only:

    python src/bot.py

Run feed-parser only:

    python src/feed.py

To stop it press:

    Control + C

Create Docker container:

    docker build -t mydealz_bot .

Run Docker container:

    docker run --env BOT_TOKEN=YOUR-TOKEN --name mydealz_bot mydealz_bot

Run Docker container in background:

    docker run --env BOT_TOKEN=YOUR-TOKEN -dit --restart unless-stopped --name mydealz_bot mydealz_bot

Stop Docker container:

    docker stop mydealz_bot

Delete Docker container:

    docker rm mydealz_bot

#### Validate code syntax with pylint

    pylint ./*.py src

#### Validate static typing

    mypy run.py
