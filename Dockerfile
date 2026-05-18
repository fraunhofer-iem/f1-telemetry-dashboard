FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./carTelemetry2val/config/carTelemetry_feeder.ini /config/carTelemetry_feeder.ini
COPY ./carTelemetry2val/carTelemetry_Kuksa2Kafka.py ./
COPY ./carTelemetry2val/carTelemetry_Kafka2InfluxDb.py ./
COPY ./kuksa-incubation/fone2val/carTelemetry_feeder.py ./

ENV PYTHONPATH=/app