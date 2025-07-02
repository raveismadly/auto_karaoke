
#!/bin/bash

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 before running this script."
    exit 1
fi

# Check if Pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: Pip 3 is not installed. Please install Pip 3 before running this script."
    exit 1
fi

# Create and activate a virtual environment

# Check for available Python versions and use 3.11 if possible

# Ensure use of available Python3 for compatibility
# Create and activate a virtual environment using the Python3 interpreter
python3 -m venv venv



# Check if Python is available in the virtual environment
if ! command -v venv/bin/python3 &> /dev/null; then
    echo "Error: Virtual environment creation failed. Please check Python installation and try again."
    exit 1
fi

# Activate the virtual environment (OS-agnostic way)
source venv/bin/activate

# Install build essentials and dependencies in the virtual environment
venv/bin/pip install setuptools wheel



# Create/update macOS-compatible virtualenv
rm -rf venv                  # Clean any existing virtual environment to avoid version conflicts
python3 -m venv venv         # Create fresh Python 3.12 virtual environment

# Activate virtualenv and upgrade pip/setuptools
source venv/bin/activate

# Upgrade system's pip in case outdated
pip install --upgrade pip

# Force compatibility requirements for Apple Silicon
brew install tcl-tk          # Homebrew installation of Tk support
xcode-select --install       # Install/verify Xcode command line tools

# Install dependencies with CCompiler resolution
venv/bin/pip install numpy==1.21.0
venv/bin/pip install setuptools==67.x.x
venv/bin/pip install -r requirements.txt


# Explicitly install numpy after pkg_resources issue resolution for macOS




# Run the main application using the virtual environment
venv/bin/python main.py

# Deactivate the virtual environment
deactivate
