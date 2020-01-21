FROM python:latest
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
ADD . /app
CMD [ "python", "./run.py" ]