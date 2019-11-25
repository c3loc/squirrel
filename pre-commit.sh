#!/usr/bin/env bash

set -eu

if [ ! -d venv ]; then
  python3.6 -m virtualenv venv
fi

source venv/bin/activate

pip install -r requirements.txt 1>/dev/null
pip install -r requirements-dev.txt 1>/dev/null

# Sort imports
isort --recursive squirrel/

# Format code
black squirrel/

# Run linting
flake8 squirrel/

# Run python tests
cd squirrel
python manage.py test -v 0
