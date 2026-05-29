
# syntax=docker/dockerfile:1
FROM python:3.11.7-slim

# Prevent Python from writing .pyc files / buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies (none required for sqlite3, it's stdlib).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

# Copy the app source
COPY . /app

# Default command runs the CLI app
CMD ["python", "main.py"]
