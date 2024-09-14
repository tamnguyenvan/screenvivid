#!/bin/bash

# Color codes for the interface
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

total_steps=6

# Function to log the current step
log_step() {
    step=$1
    step_title=$2
    echo -e "${YELLOW}[$step/$total_steps] - $step_title${NC}"
}

# Function to handle errors
handle_error() {
    error_message=$1
    echo -e "${RED}Error: $error_message${NC}"
    exit 1
}

# Function to log success messages
log_success() {
    success_message=$1
    echo -e "${GREEN}$success_message${NC}"
}

# Function to check the Python version
check_python_version() {
    log_step 1 "Checking Python version"
    if command -v python3 &>/dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        if [[ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" = "3.9" ]]; then
            log_success "Python version $python_version detected"
            return 0
        else
            handle_error "Python version 3.9 or higher is required. Your version: $python_version"
        fi
    else
        handle_error "Python 3 is not installed. Please install Python 3.9 or higher."
    fi
}

# Function to create a virtual environment
create_virtual_environment() {
    log_step 2 "Creating virtual environment"
    python3 -m venv "$HOME/.local/screenvivid_env" || handle_error "Failed to create virtual environment."
    source "$HOME/.local/screenvivid_env/bin/activate" || handle_error "Failed to activate virtual environment."
}

# Function to install the application
install_app() {
    log_step 3 "Installing ScreenVivid"
    if [ ! -d "$HOME/.local/screenvivid_env/screenvivid" ]; then
        git clone --quiet https://github.com/tamnguyenvan/screenvivid.git "$HOME/.local/screenvivid_env/screenvivid" || handle_error "Failed to clone the repository."
    fi