#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations automatically
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

echo "Build completed successfully!"