FROM python:3.11-slim

USER root

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y python3-pip gcc libpq-dev default-jre \
    && pip3 install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PYTHONPATH=/app
