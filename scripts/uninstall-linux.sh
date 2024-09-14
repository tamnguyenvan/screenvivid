#!/bin/bash

# Remove the startup script
rm -f $HOME/.local/bin/screenvivid

# Remove the virtual environment
rm -rf $HOME/.local/screenvivid_env

# Remove the desktop entry
rm -f $HOME/.local/share/applications/screenvivid.desktop

# Remove the icon
rm -f $HOME/.local/share/icons/screenvivid.png

echo "ScreenVivid has been uninstalled."