#!/bin/bash
# Activate the virtual environment
source /home/claudio/dev/imax-movies/venv/bin/activate

# Go to project directory
cd /home/claudio/dev/imax-movies/

# Run the script
python check-movies-json.py

# Git operations
git add movies.json
git commit -m "Update movies.json" || exit 0
git push

# Deactivate virtual environment
deactivate
