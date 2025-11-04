#!/bin/bash

# Navigate to the project directory
cd /home/pi/transit-board

# Activate virtual environment
source venv/bin/activate

# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Update Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Pull latest changes from git repository
git fetch origin
git pull origin main

# Run the main script
python3 main.py