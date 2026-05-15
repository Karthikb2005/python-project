# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies (including FFmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:app"]
