# ✅ Official Playwright base image
FROM mcr.microsoft.com/playwright/python:v1.45.0

# Working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port for Flask
EXPOSE 5000

# Install browsers (Chromium, etc.)
RUN playwright install

# Start app with Gunicorn
CMD ["gunicorn", "auth_server:app", "--bind", "0.0.0.0:5000"]
