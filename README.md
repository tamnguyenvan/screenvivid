![ScreenVivid](./assets/banner.svg)

<br>
<br>

ScreenVivid is a powerful and user-friendly screen recording application that allows you to capture your screen and enhance your recordings with intuitive editing features.
## Table of Contents

- [Features](#features)
- [Installation Guide](#installation-guide)
  - [System Requirements](#system-requirements)
  - [Linux Installation](#linux-installation)
  - [Windows Installation](#windows-installation)
  - [MacOS Installation](#macos-installation)
  - [Troubleshooting Installation](#troubleshooting-installation)
- [Advantages](#advantages)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Support](#support)
- [License](#license)

## Features

- Screen recording with high quality output
- Video enhancement tools (backgrounds, padding, etc.)
- User-friendly interface
- Cross-platform support (Ubuntu/Debian and Windows)

## Installation Guide

### System Requirements

- **Ubuntu/Debian**:
  - The app is based on PySide6, which requires glibc-2.28+. It supports Ubuntu 20.04 or later, Debian 10 or later, and other distributions with glibc 2.28+ such as Fedora 29+, CentOS 8+, and OpenSUSE Leap 15.1+.
  - 4GB RAM (8GB recommended)
- **Windows**:
  - Windows 10 or later
  - 4GB RAM (8GB recommended)

### Linux Installation

1. Install system dependecies if needed:
   ```bash
   # Debian/Ubuntu-based (e.g., Ubuntu, Linux Mint)
   sudo apt-get install curl git python3-tk python3-dev python3-venv libxcb-cursor0 -y

   # Fedora/CentOS 8 and later (Red Hat-based)
   sudo dnf install curl git python3-tkinter python3-devel python3-venv xcb-util-cursor -y
   ```

2. Install ScreenVivid:

   ```bash
   curl -sL https://github.com/tamnguyenvan/screenvivid/raw/main/scripts/install-linux.sh | bash
   ```

After the installation finished, you can search `ScreenVivid` in Appplication menu and use it. You can also run `screenvivid` on a new terminal.

### Windows Installation

1. Download the latest .exe installer from our official website.

2. Right-click the downloaded file and select "Run as administrator".

3. Follow the installation wizard:
   - Choose installation directory
   - Select start menu folder
   - Choose additional tasks (create desktop shortcut, etc.)

4. Click "Install" and wait for the process to complete.

5. Launch ScreenVivid from the Start menu or desktop shortcut.

### MacOS Installation
1. Install system dependecies if needed:
```bash
brew install curl git python3 tcl-tk
```
2. Install ScreenVivid:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## FAQs


## Advantages

- Easy to use
- Cross-platform
- Intuitive and simple interface
- Completely free
- Lightweight and fast

## Current Limitations

- Advanced features like zoom, audio capture, and webcam integration are not yet available.

## Roadmap

We're constantly working to improve ScreenVivid. Here are some features we're planning to add in the future:
- [ ] Advanced editing features (zoom, audio, webcam integration)

## Support

If you encounter any issues or have questions, please:

1. Check our [FAQ](#faqs)
2. Visit our [community forums](https://discord.gg/NKtmBnR6nE)
3. Contact us at tamnnv.work@gmail.com

## License

ScreenVivid is released under the MIT License. See the LICENSE file for more details.

---

Thank you for choosing ScreenVivid for your screen recording needs! If you find our software helpful, please consider donating to support its development and help us add more amazing features! 💖