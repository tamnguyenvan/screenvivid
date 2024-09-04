#!/bin/bash

check_python_version() {
    if command -v python3 &>/dev/null; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
        if [ "$(printf '%s\n' "3.9" "$python_version" | sort -V | head -n1)" = "3.9" ]; then
            echo "Python version $python_version is installed and meets the minimum requirement."
        else
            echo "Error: Python version 3.9 or higher is required. Your version: $python_version"
            exit 1
        fi
    else
        echo "Error: Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi
}

create_virtual_environment() {
    echo "Creating virtual environment..."
    python3 -m venv "$HOME/.local/screenvivid_env"
    source "$HOME/.local/screenvivid_env/bin/activate"
}

install_app() {
    echo "Installing ScreenVivid..."
    git clone https://github.com/tamnguyenvan/screenvivid.git $HOME/.local/screenvivid_env/screenvivid
    cd $HOME/.local/screenvivid_env/screenvivid && pip install -r requirements.txt
}

create_startup_script() {
    echo "Creating startup script..."
    cat > "$HOME/.local/bin/screenvivid" << EOL
#!/bin/bash
source "$HOME/.local/screenvivid_env/bin/activate"
python -m screenvivid.main
EOL
    chmod +x "$HOME/.local/bin/screenvivid"
}

create_desktop_file() {
    echo "Creating desktop entry..."
    cat > "$HOME/.local/share/applications/screenvivid.desktop" << EOL
[Desktop Entry]
Name=ScreenVivid
Exec=/home/tamnv/.local/bin/screenvivid
Icon=/home/tamnv/.local/share/icons/screenvivid.png
Type=Application
Categories=Utility;
Comment=ScreenVivid Application
EOL
}

download_icon() {
    echo "Downloading application icon..."
    icon_url="https://raw.githubusercontent.com/tamnguyenvan/screenvivid/main/screenvivid/resources/icons/screenvivid.png"
    icon_path="$HOME/.local/share/icons/screenvivid.png"
    mkdir -p "$(dirname "$icon_path")"
    curl -o "$icon_path" "$icon_url"
}

check_python_version
create_virtual_environment
install_app
create_startup_script
create_desktop_file
download_icon

echo "Installation completed. You can now find and run ScreenVivid from your application menu."
