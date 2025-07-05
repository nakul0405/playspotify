# ✅ Use official Playwright base image
FROM mcr.microsoft.com/playwright/python:v1.45.0

# Set working directory
WORKDIR /app

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Expose port (Flask default)
EXPOSE 5000

# ✅ Install Playwright browsers
RUN playwright install

# Start the Flask server
CMD ["python", "auth_server.py"]
