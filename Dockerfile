FROM python:2.7

RUN apt-get update && apt-get install -y python-dev build-essential
RUN pip install --upgrade pip

ADD . /code
COPY requirements.txt /code
WORKDIR /code

RUN pip install -r requirements.txt

EXPOSE 5000

