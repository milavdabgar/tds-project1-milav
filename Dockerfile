# Use Python 3.11 image
FROM python:3.11

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    git \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Install prettier globally
RUN npm install -g prettier@3.4.2

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create entrypoint script
RUN echo '#!/bin/sh\n\
python datagen.py 21f1005510@ds.study.iitm.ac.in\n\
exec uvicorn app:app --host 0.0.0.0 --port 8000\n' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
