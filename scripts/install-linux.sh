#!/bin/bash

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Unicode characters
CHECK_MARK='\u2714'
CROSS_MARK='\u2718'
ARROW='\u2192'

total_steps=6

log_step() {
    step=$1
    step_title=$2
    printf "${BLUE}[%s/%s]${NC} ${ARROW} ${YELLOW}%s${NC}\n" "$step" "$total_steps" "$step_title"
}

handle_error() {
    error_message=$1
    printf "${RED}${CROSS_MARK} Error: %s${NC}\n" "$error_message"
    exit 1
}

log_success() {
    message=$1
    printf "${GREEN}${CHECK_MARK} %s${NC}\n" "$message"
}

check_python_version() {
    log_step 1 "Checking Python version"
    if command -v python3 &>/dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        if [ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" = "3.9" ]; then
            log_success "Python version $python_version detected"
            return 0
        else
            handle_error "Python version 3.9 or higher is required. Your version: $python_version"
        fi
    else
        handle_error "Python 3 is not installed. Please install Python 3.9 or higher."
    fi
}

create_virtual_environment() {
    log_step 2 "Creating virtual environment"
    python3 -m venv "$HOME/.local/screenvivid_env" || handle_error "Failed to create virtual environment."
    source "$HOME/.local/screenvivid_env/bin/activate" || handle_error "Failed to activate virtual environment."
    log_success "Virtual environment created and activated"
}

install_app() {
    log_step 3 "Installing ScreenVivid"
    if [ ! -d $HOME/.local/screenvivid_env/screenvivid ]; then
        git clone --quiet https://github.com/tamnguyenvan/screenvivid.git $HOME/.local/screenvivid_env/screenvivid || handle_error "Failed to clone the repository."
    fi
    cd $HOME/.local/screenvivid_env/screenvivid || handle_error "Failed to navigate to the ScreenVivid directory."
    pip install "python-xlib>=0.33,<1.0" -q -q -q --exists-action i || handle_error "Failed to install required packages."
    pip install -r requirements.txt -q -q -q --exists-action i || handle_error "Failed to install required packages."
    log_success "ScreenVivid installed successfully"
}

create_startup_script() {
    log_step 4 "Creating startup script"
    mkdir -p $HOME/.local/bin
    cat > "$HOME/.local/bin/screenvivid" << EOL
#!/bin/bash
source "$HOME/.local/screenvivid_env/bin/activate"
cd $HOME/.local/screenvivid_env/screenvivid
python -m screenvivid.main
EOL
    chmod +x "$HOME/.local/bin/screenvivid" || handle_error "Failed to make the startup script executable."
    log_success "Startup script created"
}

add_local_bin_to_path() {
    log_step 5 "Adding ~/.local/bin to PATH"
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        source "$HOME/.bashrc" || handle_error "Failed to reload .bashrc"
    fi
    log_success "~/.local/bin added to PATH"
}

create_desktop_file() {
    log_step 6 "Creating desktop entry"
    mkdir -p $HOME/.local/share/applications
    cat > "$HOME/.local/share/applications/screenvivid.desktop" << EOL
[Desktop Entry]
Name=ScreenVivid
Exec=$HOME/.local/bin/screenvivid
Icon=$HOME/.local/share/icons/screenvivid.png
Type=Application
Categories=Utility;
Comment=ScreenVivid Application
EOL
    log_success "Desktop entry created"
}

download_icon() {
    icon_url="https://raw.githubusercontent.com/tamnguyenvan/screenvivid/main/screenvivid/resources/icons/screenvivid.png"
    icon_path="$HOME/.local/share/icons/screenvivid.png"
    mkdir -p "$(dirname "$icon_path")" || handle_error "Failed to create directory for the icon."
    curl -sS -o "$icon_path" "$icon_url" || handle_error "Failed to download the application icon."
    log_success "Application icon downloaded"
}

# Main installation process
printf "${YELLOW}=== ScreenVivid Installation ===${NC}\n\n"

check_python_version
create_virtual_environment
install_app
create_startup_script
add_local_bin_to_path
create_desktop_file
download_icon

printf "\n${GREEN}${CHECK_MARK} Installation completed successfully.${NC}\n"
printf "${BLUE}${ARROW} You can now find and run ScreenVivid from your application menu.${NC}\n"