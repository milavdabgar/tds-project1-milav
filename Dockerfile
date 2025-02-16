# Use Python 3.11 image
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    iputils-ping \
    ffmpeg \
    libportaudio2 \
    libavcodec-extra \
    && rm -rf /var/lib/apt/lists/*

# Install prettier and ensure npx is available
RUN npm install -g prettier@3.4.2 && \
    chmod +x $(which npx) && \
    npm config set prefix /usr/local

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /data

# Copy application code
COPY . .

# Create entrypoint script
RUN echo '#!/bin/sh\n\
if [ -z "$EMAIL" ]; then\n\
  EMAIL=user@example.com\n\
fi\n\
python datagen.py "$EMAIL" || true\n\
exec uvicorn app:app --host 0.0.0.0 --port 8000\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
