# AutoKaraoke Installation Script for macOS

set -e  # Exit on error

echo "=== AutoKaraoke Installer for macOS ==="
echo "This script will install AutoKaraoke and its dependencies."

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "Error: This script is intended for macOS only."
    exit 1
fi

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install ffmpeg and python if not already installed
echo "Installing system dependencies..."
brew install ffmpeg python@3.10

# Create a virtual environment
echo "Creating Python virtual environment..."
/opt/homebrew/opt/python@3.10/bin/python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install the package
echo "Installing AutoKaraoke..."
pip install -e .

echo ""
echo "=== Installation Complete ==="
echo "To activate the virtual environment, run:"
echo "source venv/bin/activate"
echo ""
echo "To start AutoKaraoke, run:"
echo "autokaraoke"
