FROM python:3.13-slim

WORKDIR /usr/src/app

COPY requirements.txt app.py ./
COPY src ./src
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./app.py" ]
