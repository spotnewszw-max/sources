#!/bin/bash

# This script is for database migrations.

# Activate the virtual environment
source ../venv/bin/activate  # Adjust the path if necessary

# Run the migration command
alembic upgrade head  # Ensure alembic is installed and configured

# Deactivate the virtual environment
deactivate