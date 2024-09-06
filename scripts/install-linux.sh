#!/bin/bash

total_steps=6

log_step() {
    step=$1
    step_title=$2
    echo "[$step/$total_steps] - $step_title"
}

handle_error() {
    error_message=$1
    echo "Error: $error_message"
    exit 1
}

check_python_version() {
    log_step 1 "Checking Python version"
    if command -v python3 &>/dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        if [ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" = "3.9" ]; then
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
}

install_app() {
    log_step 3 "Installing ScreenVivid"
    if [ ! -d $HOME/.local/screenvivid_env/screenvivid ]; then
        git clone --quiet https://github.com/tamnguyenvan/screenvivid.git $HOME/.local/screenvivid_env/screenvivid || handle_error "Failed to clone the repository."
    fi
    cd $HOME/.local/screenvivid_env/screenvivid || handle_error "Failed to navigate to the ScreenVivid directory."
    pip install -r requirements.txt -q -q -q --exists-action i || handle_error "Failed to install required packages."
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
}

add_local_bin_to_path() {
    log_step 5 "Adding ~/.local/bin to PATH"
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        source "$HOME/.bashrc" || handle_error "Failed to reload .bashrc"
    fi
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
}

download_icon() {
    icon_url="https://raw.githubusercontent.com/tamnguyenvan/screenvivid/main/screenvivid/resources/icons/screenvivid.png"
    icon_path="$HOME/.local/share/icons/screenvivid.png"
    mkdir -p "$(dirname "$icon_path")" || handle_error "Failed to create directory for the icon."
    curl -sS -o "$icon_path" "$icon_url" || handle_error "Failed to download the application icon."
}

# Execute the steps
check_python_version
create_virtual_environment
install_app
create_startup_script
add_local_bin_to_path
create_desktop_file
download_icon

echo "Installation completed successfully. You can now find and run ScreenVivid from your application menu."
