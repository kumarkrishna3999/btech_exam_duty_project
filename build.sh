#!/usr/bin/env bash

<<<<<<< HEAD
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
=======
pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py migrate
>>>>>>> 8d9e48811fb414962ba8ebd80ba0d6ccd30a8213
