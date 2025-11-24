# backend/Dockerfile
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set working directory in container
WORKDIR /app

# Install system deps (optional but safer for scientific libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure data/models directories exist inside container
RUN mkdir -p data/raw data/processed models

# Copy backend source code
COPY app ./app
# If you have local data/models you want in the image, uncomment:
# COPY data ./data
# COPY models ./models

# Expose FastAPI port
EXPOSE 8000

# Default command: run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
