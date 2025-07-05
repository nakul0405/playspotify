# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for auth_server
EXPOSE 8000

# Start both bot and auth server together
CMD ["bash", "start.sh"]
