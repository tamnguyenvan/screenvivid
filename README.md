![ScreenVivid Banner](./assets/banner.svg)

<br>
<br>

## Overview

ScreenVivid is a powerful and user-friendly screen recording application designed to help you capture your screen and enhance your recordings with intuitive editing features. Whether you're creating tutorials, recording meetings, or capturing gameplay, ScreenVivid is the perfect tool for you.

## Table of Contents

- [Features](#features)
- [Installation Guide](#installation-guide)
  - [System Requirements](#system-requirements)
  - [Linux Installation](#linux-installation)
  - [Windows Installation](#windows-installation)
  - [MacOS Installation](#macos-installation)
- [Advantages](#advantages)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Support](#support)
- [License](#license)

## Features

- **Cross-platform support**: ScreenVivid is available on MacOS, Windows, and Ubuntu/Debian, ensuring you can record your screen regardless of your operating system.
- **High-quality screen recording**: Capture your screen with high-quality output, perfect for creating professional-looking videos.
- **Free and open-source**: ScreenVivid is completely free to use and open-source, allowing the community to contribute and improve the application.
- **Video enhancement tools**: Enhance your recordings with backgrounds, padding, and other intuitive editing features.
- **Intuitive and simple interface**: ScreenVivid's user-friendly interface makes it easy to start recording and editing your screen captures.

![ScreenVivid UI Showcase](./assets/showcase.png)

## Installation Guide

### System Requirements

- **Ubuntu/Debian**:
  - **Minimum Requirements:** Ubuntu 20.04 or later, Debian 10 or later, 4GB RAM (8GB recommended)
  - **Compatibility Note:** ScreenVivid is designed to work seamlessly with X11-based systems, ensuring a smooth experience on Ubuntu and Debian.
- **Windows**:
  - **Minimum Requirements:** Windows 10 or later, 4GB RAM (8GB recommended)
- **MacOS**:
  - **Minimum Requirements:** MacOS 10.15 or later, 4GB RAM (8GB recommended)

### Linux Installation
Download the latest .deb package from our [Releases page](https://github.com/tamnguyenvan/screenvivid/releases).
```bash
# Debian/Ubuntu (apt-get)
sudo dpkg -i screenvivid_x.x.x_amd64.deb
```

### Windows Installation

1. Download the latest .exe installer from our [Releases page](https://github.com/tamnguyenvan/screenvivid/releases).
2. If Windows displays a warning during download, click "Keep anyway" to proceed.
3. Run the installer. If you see a SmartScreen warning, click "More info" and then "Run anyway" to continue.
4. Follow the installation prompts to complete the setup.
5. Launch the program from your Start Menu or the newly created Desktop shortcut.

🚨 **Important Note**: Due to current budget constraints, our application is not code-signed. This may trigger Windows security warnings, but rest assured that our software is safe to use. We're working on obtaining a code signing certificate in the future to eliminate these warnings.


### MacOS Installation
Download the latest .dmg package from our [Releases page](https://github.com/tamnguyenvan/screenvivid/releases).

1. Open the DMG file and drag the ScreenVivid icon to the Applications folder.
2. Run the app from your Applications folder.

🚨 **Important Note:** As the app is not notarized, Gatekeeper may display a warning. To proceed, go to System `Settings > Privacy & Security > Security`, select "Open Anyway", and confirm with your login password. For more information, please refer to [this guide](https://support.apple.com/en-vn/guide/mac-help/mchleab3a043/mac).

### Running from Source

For systems without installation file support, ScreenVivid can be run using Python by following these steps:

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
# Ubuntu/Debian
sudo apt-get install python3-tk libxcb-cursor0

# MacOS

# Assuming you're in the root of the repository
python -m screenvivid.main
```

## FAQs


## Advantages

- **Easy to use**: ScreenVivid's intuitive interface makes it easy to start recording and editing your screen captures.
- **Cross-platform**: Available on MacOS, Windows, and Ubuntu/Debian, ensuring you can record your screen regardless of your operating system.
- **Intuitive and simple interface**: ScreenVivid's user-friendly interface makes it easy to start recording and editing your screen captures.
- **Completely free**: ScreenVivid is completely free to use and open-source, allowing the community to contribute and improve the application.
- **Lightweight and fast**: ScreenVivid is designed to be lightweight and fast, ensuring a smooth recording experience.

## Current Limitations

- **Advanced features**: Advanced features like zoom, audio capture, and webcam integration are not yet available.

## Roadmap

We're constantly working to improve ScreenVivid. Here are some features we're planning to add in the future:
- [ ] **Advanced editing features**: Zoom, audio capture, and webcam integration.

## Support

If you encounter any issues or have questions, please:

1. Check our [FAQ](#faqs)
2. Visit our [community forums](https://discord.gg/NKtmBnR6nE)
3. Contact us at tamnnv.work@gmail.com

## License

ScreenVivid is released under the MIT License. See the LICENSE file for more details.

---

Thank you for choosing ScreenVivid for your screen recording needs! If you find our software helpful, please consider donating to support its development and help us add more amazing features! 💖