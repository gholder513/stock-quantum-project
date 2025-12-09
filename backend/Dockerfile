# backend/Dockerfile
FROM python:3.11-slim

# ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for scientific libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# requirements.txt lives in backend/
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure data/models dirs exist inside container
RUN mkdir -p data/raw data/processed models

# Backend source code lives in backend/app
COPY backend/app ./app

# only wanted the processed data and models in the container(don't need raw data for production, only dev)
COPY backend/data/processed ./backend/data/processed
COPY models ./models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
