FROM python:3.10.6

ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

COPY . /app

RUN mkdir /app/avatars

RUN pip install -r requirments.txt