


# Ensure the script is executable
chmod +x ./launch.sh


#!/bin/bash


# Set architecture flags
export ARCHFLAGS="-arch arm64 -arch x86_64"

# Check if Homebrew is installed and prompt for installation
if ! command -v brew &> /dev/null; then
    echo "Warning: Homebrew not found and installation is recommended for missing dependencies."
    read -p "Press enter to proceed without Homebrew " DUMMY
fi

# Remove existing virtual environment
rm -rf venv




# Check if Homebrew is installed and prompt for installation
if ! command -v brew &> /dev/null; then
    echo 'Warning: Homebrew not found. Installing libsndfile and ffmpeg may require Homebrew'
    echo 'Run "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""'
    echo 'Press [ENTER] to continue without Homebrew installation...'
    read DUMMY
fi





#!/bin/bash

# Attempt to fix Python 3.8 dependencies
if ! command -v brew &> /dev/null; then
    if ! command -v python3.8 &> /dev/null; then
        echo "Warning: Homebrew not found but needed to manage ffmpeg/libsndfile/numpy dependencies"


export PYCFLAGS="-I/usr/local/include -L/usr/local/lib"
export CFLAGS="$PYCFLAGS -arch arm64 -arch x86_64"
export LDFLAGS="$PYCFLAGS -framework Accelerate"


        read -p "Press enter to proceed (may cause installation errors)" DUMMY
    else
        echo "Proceeding without Homebrew as Python 3.8.x is installed in environment: $(command -v python3.8 | cut -f2 -d' ')"
    fi
fi



set -e

# Export architecture flags
export ARCHFLAGS="-arch arm64 -arch x86_64"


# Attempt to install Python 3.8 if missing
if ! command -v pyenv &> /dev/null || ! pyenv versions | grep -q 3.8.15; then
    echo "Installing Python 3.8.15 via pyenv (requires internet connection)..."
    pyenv install 3.8.15
    pyenv global 3.8.15
    echo "Python version set to 3.8.15"
fi


# Add shared libraries and headers to LIBRARY_PATH and CPATH
export LIBRARY_PATH=$LIBRARY_PATH:/usr/local/lib
export CPATH=$CPATH:/usr/local/include



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

# Set up C compiler environment for Python 3.12 ARM64
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



# Ensure all environment variables are set for proper package compilation
export CPATH=/usr/local/include:$CPATH
export LIBRARY_PATH=/usr/local/lib:$LIBRARY_PATH


# Ensure use of available Python3 for compatibility
# Create and activate a virtual environment using the Python3 interpreter
python3 -m venv venv



# Check if Python is available in the virtual environment
if ! command -v venv/bin/python$python_version &> /dev/null; then


# Set Python 3.11 as default
python_version="3.8"

echo "Creating Python 3.8-specific ARM64-optimized environment..."

# Set Python 3.8 as default (ensure it is installed)
python_version="3.8"
echo "Creating Python 3.8-specific ARM64-optimized environment..."
if command -v python3.8 &> /dev/null; then
    deactivate &>/dev/null
    python3.8 -m venv venv
    source venv/bin/activate
else
    echo "Python 3.8 is not installed on your system. Please install Python 3.8 to proceed."
    exit 1
fi
pip install --upgrade pip setuptools wheel


python$python_version -m venv venv
source venv/bin/activate

echo "Updating pip..."
pip install --upgrade pip setuptools wheel numpy==1.21.1



    echo "Error: Virtual environment creation failed. Please check Python installation and try again."
    exit 1
fi


# Verify Python 3.11 installation and required binaries
vpython=$(venv/bin/python --version)
if ! echo "$vpython" | grep -q "3\.8"; then
    echo "Error: The virtual environment is not using Python 3.8. Please check the installation."
    exit 1
fi




# Install remaining packages explicitly to overcome setuptools issues


# Pinning numpy and setuptools versions to stable builds first
venv/bin/pip install numpy==1.18.5 setuptools==59.5.0 pip==22.0.4



venv/bin/pip install numpy==1.21.1 librosa==0.8.1 spleeter==2.1.0



# Retry Numpy and spleeter installations if needed
if ! venv/bin/pip show numpy > /dev/null; then
    echo "Retrying installation of numpy with Python 3.11 and pip dependencies..."
    venv/bin/pip install --no-cache-dir numpy==1.21.1
fi

if ! venv/bin/pip show spleeter > /dev/null; then
    echo "Retrying installation of spleeter with Python 3.11 and pip dependencies..."
    venv/bin/pip install --no-cache-dir spleeter==2.1.0
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


pip install -r requirements.txt


# Explicitly install numpy after pkg_resources issue resolution for macOS




# Run the main application using the virtual environment
venv/bin/python main.py

# Deactivate the virtual environment
deactivate
