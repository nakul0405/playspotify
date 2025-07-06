# Use official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y curl

# Copy files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask server port
EXPOSE 10000

# Run both Flask and Telegram bot
CMD ["bash", "start.sh"]
