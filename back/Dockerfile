FROM python:3.13-slim

# Install FFmpeg and basic system dependencies.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*


# Application directory.
WORKDIR /app


# Install Python dependencies.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Copy application.
COPY app.py .


# Render provides PORT.
ENV PORT=10000


# Start Flask through Gunicorn.
CMD gunicorn \
    --bind 0.0.0.0:${PORT} \
    --workers 1 \
    --timeout 3600 \
    app:app
