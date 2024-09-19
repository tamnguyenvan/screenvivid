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

![ScreenVivid UI](./assets/showcase.png)

## Installation Guide

### System Requirements

- **Ubuntu/Debian**:
  - The app is based on PySide6, which requires glibc-2.28+. It supports Ubuntu 20.04 or later, Debian 10 or later.
  - 4GB RAM (8GB recommended)
  - **ScreenVivid uses [python-mss](https://github.com/BoboTiG/python-mss) to capture the screen, making it compatible only with operating systems that use X11.**
- **Windows**:
  - Windows 10 or later
  - 4GB RAM (8GB recommended)
- **MacOS**:
  - MacOS 10.15 or later
  - 4GB RAM (8GB recommended)

### Linux Installation
Download the latest .deb package or .rpm package from our [Releases page](https://github.com/tamnguyenvan/screenvivid/releases).
```bash
# Debian/Ubuntu (apt-get)
sudo dpkg -i screenvivid_x.x.x_amd64.deb
```

### Windows Installation

1. Grab the latest .exe installer from our [Releases page](https://github.com/tamnguyenvan/screenvivid/releases).
2. When downloading, Windows may display a warning. Click "Keep anyway" to proceed with the download.
3. Run the installer. You may see a SmartScreen warning. Click "More info" and then "Run anyway" to continue.
4. Follow the installation prompts to complete the setup.
5. Launch the program from your Start Menu or the newly created Desktop shortcut.

Note: Due to current budget constraints, our application is not code-signed. This may trigger Windows security warnings, but rest assured that our software is safe to use. We're working on obtaining a code signing certificate in the future to eliminate these warnings.


### MacOS Installation

Download the latest .dmg package from our [Releases page](https://github.com/tamnguyenvan/screenvivid/releases).

1. Open the DMG file and drag the ScreenVivid icon to the Applications folder.
2. Run the app from your Applications folder.


### From source

1. Clone the repository
```bash
git clone https://github.com/tamnguyenvan/screenvivid.git
```
2. Install dependencies
```bash
pip install -r requirements.txt
```
3. Compile resources (Optional)
```bash
cd screenvivid
python compile_resources.py
```

4. Run the app
```bash
# Assume you're in the root of the repo
python -m screenvivid.main
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