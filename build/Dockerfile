# Debian base image
FROM python:3.12.9-slim-bookworm

# Get apt sources and install ghostscript
RUN apt-get update && apt-get install -y ghostscript zbar-tools imagemagick qpdf unzip

# Create a group and a user fastapi
RUN groupadd -r fastapi && useradd -r -g fastapi fastapi

# Create a working directory and change ownership
WORKDIR /app
RUN chown -R fastapi:fastapi /app

# Copy app to to container
COPY /src .
COPY /build/policy.xml /etc/ImageMagick-6

# Upgrade pip first to newest version and install all requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose Port 8080 to ouside world resp. host system
EXPOSE 8080

# Change user
USER fastapi

# Run command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
