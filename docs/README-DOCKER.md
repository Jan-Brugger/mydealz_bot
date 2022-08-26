# mydealz_bot
This is a Docker container to run a telegram bot that tracks mydealz.de for new deals.

## Command line

    docker run -d --name=mydealz_bot \
    --restart=always \
    -v /opt/mydealz_bot/files:/usr/src/app/files \
    -v /etc/localtime:/etc/localtime:ro \
    --env BOT_TOKEN=<<YOUR_BOT_TOKEN>> \
    weltraumpenner/mydealz_bot:latest

### Command line Options

| Parameter                                    | Description                                                                                                               |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| --restart=always                             | Start the container when Docker starts (i.e. on boot/reboot).                                                             |
| -v /opt/mydealz_bot/files:/usr/src/app/files | Mount directory /usr/src/app/files from host machine. This directory contains the database, persistent chat-data and logs |
| -v /etc/localtime:/etc/localtime:ro          | Use correct timezone from docker-host                                                                                     |
| --env BOT_TOKEN=<<YOUR_BOT_TOKEN>>           | Your telegram-bot token. You can create one with @BotFather                                                               |
| --env OWN_ID=<<YOUR_TELEGRAM_ID>>            | Your telegram-user-id. It's used to forward error-messages                                                                |
| --env PARSE_INTERVAL=<<INTERVAL>>            | How often new deals should be fetched (in seconds)                                                                        |
| --env NOTIFICATION_CAP=<<CAP>>               | How many notifications user can create                                                                                    |
| --env RESTRICT_ACCESS=<<ACCESS>>             | Restricted Access, so that users can be blocked (False for public Bot, True for private Bot)                              |

### docker-compose.yaml

    version: '3'
    services:
      mydealz:
        container_name: mydealz
        image: weltraumpenner/mydealz_bot:latest
        restart: always
        volumes:
          - /opt/mydealz_bot/files:/usr/src/app/files
          - /etc/localtime:/etc/localtime:ro
        environment:
          - BOT_TOKEN=<<YOUR_BOT_TOKEN>>
          - OWN_ID=<<YOUR_TELEGRAM_ID>>

### Troubleshooting

**"can't initialize time"-error on Raspberry Pi**

Update libseccomp2.deb
- Find latest libseccomp2.deb on http://ftp.us.debian.org/debian/pool/main/libs/libseccomp

- Download and install

      cd /tmp
      wget http://ftp.us.debian.org/debian/pool/main/libs/libseccomp/libseccomp2_2.5.0-3_armhf.deb
      sudo dpkg -i libseccomp2_2.5.0-3_armhf.deb
