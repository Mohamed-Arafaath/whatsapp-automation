#!/bin/bash

# Exit on error
set -e

echo "Installing Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update
apt-get install -y google-chrome-stable

echo "Chrome installed at: $(which google-chrome)"

# Install ChromeDriver
echo "Installing ChromeDriver..."
CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip
unzip -o chromedriver_linux64.zip
chmod +x chromedriver
mv -f chromedriver /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

echo "ChromeDriver installed"
