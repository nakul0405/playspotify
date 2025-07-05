FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# System packages for Playwright + Chrome deps
RUN apt-get update && apt-get install -y \
    wget git ffmpeg \
    libglib2.0-0 libnss3 libgconf-2-4 libxss1 libasound2 libxtst6 \
    libatk-bridge2.0-0 libgtk-3-0 libdrm2 libxcomposite1 libxrandr2 \
    libxdamage1 libgbm1 libpango-1.0-0 libpangocairo-1.0-0 \
    fonts-liberation libappindicator3-1 xdg-utils \
    curl gnupg ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Install Playwright browsers
RUN playwright install --with-deps

# Start both Flask and Bot using start.sh
CMD ["bash", "start.sh"]
