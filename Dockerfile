# Use official lightweight Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy entire project
COPY . .

# Give execution permission to start.sh (if needed)
RUN chmod +x start.sh

# Start the bot using bash script
CMD ["bash", "start.sh"]
