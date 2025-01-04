#!/bin/bash

# Update the package list and upgrade existing packages
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install -y python3 python3-pip

# Install Apache server
sudo apt install -y apache2

# Enable and start Apache service
sudo systemctl enable apache2
sudo systemctl start apache2

# Clone the repository
git clone https://github.com/BohBOhTN/ELKOLLA_API.git

echo "Python installed, Apache server set up, and repository cloned successfully!"
