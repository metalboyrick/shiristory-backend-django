FROM python:3.8-slim

WORKDIR /course/code

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt