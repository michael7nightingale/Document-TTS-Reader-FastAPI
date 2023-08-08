FROM python:3.11

COPY app ./app
COPY requirements.txt ./requirements.txt
COPY .docker.env ./.docker.env

RUN pip install -r requirements.txt

EXPOSE 8000
