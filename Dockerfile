FROM python:3.8-slim

WORKDIR /course/code

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt