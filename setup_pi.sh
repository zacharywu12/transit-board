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
cd /home/pi
python3 -m venv venv
source venv/bin/activate

# Clone the repository
echo "Cloning the repository..."
git clone git@github.com:zacharywu12/transit-private.git transit-board
cd transit-board

# Install Python packages
echo "Installing Python packages..."
pip3 install --no-cache-dir -r requirements.txt

# Make startup script executable
chmod +x startup.sh

# Set up systemd service for auto-start
echo "Setting up auto-start service..."
sudo tee /etc/systemd/system/transit-board.service << EOF
[Unit]
Description=Transit Board Display
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/transit-board
ExecStart=/bin/bash /home/pi/transit-board/startup.sh
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl enable transit-board.service
sudo systemctl start transit-board.service

echo "Setup complete! The transit board will now:"
echo "1. Start automatically on boot"
echo "2. Update system and packages"
echo "3. Pull latest code changes"
echo "4. Run the display"
echo ""
echo "To check status: sudo systemctl status transit-board"
echo "To view logs: journalctl -u transit-board -f"