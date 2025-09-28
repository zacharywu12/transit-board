#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-pandas \
    libatlas-base-dev \
    python3-protobuf \
    git

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip3 install --no-cache-dir \
    pandas \
    requests \
    gtfs-realtime-bindings \
    protobuf

# Clone the repository (if not already done)
# if [ ! -d "transit-board" ]; then
#     git clone https://github.com/zacharywu12/transit-board.git
# fi

echo "Setup complete! To run the transit board:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the script: python3 muni.py"