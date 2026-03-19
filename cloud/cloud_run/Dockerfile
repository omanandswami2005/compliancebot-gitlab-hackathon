# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY report_generator.py .

# Set environment variables
ENV PYTHONUNBUFFERED=True \
    PORT=8080

# Run the application with gunicorn
CMD exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 8 --timeout 0 report_generator:app
