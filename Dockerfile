FROM alpine:latest

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 py-pip py-cryptography && ln -sf python3 /usr/bin/python

WORKDIR /usr/src/app

COPY requirements.txt daemon.py ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./daemon.py" ]
