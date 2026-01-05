# Multi-stage Dockerfile for production
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y     build-essential     && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY docker_monitor/requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy API code
COPY docker_monitor/app ./app

# Copy model
COPY docker_monitor/models ./models

EXPOSE 8000 9090

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
