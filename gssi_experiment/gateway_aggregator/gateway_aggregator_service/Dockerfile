# syntax=docker/dockerfile:1

FROM python:3.11

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
ENV PYTHONPATH "/app/base:/app/gateway_aggregator_service"

# Installs python dependencies etc.
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . /app/

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
