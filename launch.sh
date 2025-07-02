
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

# Verify Python architecture

# Set up CCompiler environment for Python 3.12 ARM64
export MACOSX_DEPLOYMENT_TARGET=11.0



# Verify Homebrew availability
if command -v brew &> /dev/null
then
    echo "Homebrew is installed. Updating and installing dependencies..."
    brew update
    brew install pkg-config ffmpeg sndfile
else
    echo "Warning: Homebrew not found. Skipping Homebrew-managed dependencies."
fi





python_arch=$(python3 -c "import platform; print(platform.machine())")
if [ "$python_arch" = "arm64" ]; then
  echo "Detected ARM64 architecture. Adjusting dependencies accordingly..."
  # Additional ARM64 specific setup
fi

# Set environment variables for CCompiler compatibility
export CFLAGS="-arch arm64"  # For ARM64 target architecture
export CPPFLAGS="$CFLAGS"    # Copy CFLAGS to C++ flags


export PYTHON_CONFIGURE_OPTS="--enable-optimizations --enable-framework --with-extra-ldflags=-L/opt/homebrew/opt/libomp/lib"



# Set up Homebrew dependencies if needed
brew update
brew install pkg-config ffmpeg sndfile




# Set specific CFLAGS/LDFLAGS for numpy and libs/whl ARM64 builds
# Set numpy compilation flags
export NPY_CFLAGS=-arch arm64
export NPY_LDFLAGS=-arch arm64


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




# Downgrade pip to avoid numpy build issues
venv/bin/pip install pip==25.0



# Create/update macOS-compatible virtualenv
rm -rf venv                  # Clean any existing virtual environment to avoid version conflicts
python3 -m venv venv         # Create fresh Python 3.12 virtual environment

# Activate virtualenv and upgrade pip/setuptools
source venv/bin/activate

# Upgrade system's pip in case outdated
pip install --upgrade pip

# Force compatibility requirements for Apple Silicon


# Install dependencies with CCompiler resolution


venv/bin/pip install -r requirements.txt


# Explicitly install numpy after pkg_resources issue resolution for macOS




# Run the main application using the virtual environment
venv/bin/python main.py

# Deactivate the virtual environment
deactivate
