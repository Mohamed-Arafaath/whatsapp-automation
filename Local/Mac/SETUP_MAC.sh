#!/bin/bash
echo "=========================================="
echo "      WHATSAPP AUTOMATION SETUP"
echo "=========================================="
echo ""

# Function to install Homebrew
install_homebrew() {
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add brew to path for immediate use
    eval "$(/opt/homebrew/bin/brew shellenv)"
}

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    read -p "Homebrew is required to automate installation. Install it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_homebrew
    else
        echo "Skipping automated installation. Please install Python and Chrome manually."
        exit 1
    fi
fi

# Install Python
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    brew install python
else
    echo "Python is already installed."
fi

# Install Chrome
if [ ! -d "/Applications/Google Chrome.app" ]; then
    echo "Installing Google Chrome..."
    brew install --cask google-chrome
else
    echo "Google Chrome is already installed."
fi

echo ""
echo "Installing Python dependencies..."

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Cannot find requirements.txt"
    echo "⚠️  Make sure you are running this script from inside the folder!"
    exit 1
fi

pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "      SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "You can now run './RUN_MAC.sh' to start the app."
echo ""
