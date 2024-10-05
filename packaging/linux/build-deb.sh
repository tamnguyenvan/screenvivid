#!/bin/bash

# Application name (lowercase for package name, mixed case for display name)
PKG_NAME="screenvivid"
DISPLAY_NAME="ScreenVivid"

# Version number
VERSION=${1:-"1.0.0"}

# Architecture
ARCH="amd64"

# Create directory structure for the .deb package
mkdir -p ${PKG_NAME}-${VERSION}-${ARCH}/DEBIAN
mkdir -p ${PKG_NAME}-${VERSION}-${ARCH}/opt/${PKG_NAME}/${PKG_NAME}
mkdir -p ${PKG_NAME}-${VERSION}-${ARCH}/usr/share/applications
mkdir -p ${PKG_NAME}-${VERSION}-${ARCH}/usr/share/icons/hicolor/256x256/apps
mkdir -p ${PKG_NAME}-${VERSION}-${ARCH}/usr/share/doc/${PKG_NAME}
mkdir -p ${PKG_NAME}-${VERSION}-${ARCH}/usr/bin

# Create the control file
cat << EOF > ${PKG_NAME}-${VERSION}-${ARCH}/DEBIAN/control
Package: ${PKG_NAME}
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Pre-Depends: libxcb-cursor0, python3-venv, python3-tk
Maintainer: DarkPhoton <tamnv.work@gmail.com>
Homepage: https://www.screenvivid.com
License: CC BY-NC-SA 4.0
Description: Screen recording and editing application
 ${DISPLAY_NAME} is a cross-platform desktop application for screen recording
 and video editing, featuring options like background replacement and padding.
EOF

# Copy the entire application directory
cp -R ../../${PKG_NAME}/* ${PKG_NAME}-${VERSION}-${ARCH}/opt/${PKG_NAME}/${PKG_NAME}
cp -R ../../requirements.txt ${PKG_NAME}-${VERSION}-${ARCH}/opt/${PKG_NAME}
cp -R ../../scripts/run ${PKG_NAME}-${VERSION}-${ARCH}/opt/${PKG_NAME}/run

# Copy the LICENSE file and rename it to 'copyright'
cp ../../LICENSE ${PKG_NAME}-${VERSION}-${ARCH}/usr/share/doc/${PKG_NAME}/copyright

# Create postinst file
cat << EOF > ${PKG_NAME}-${VERSION}-${ARCH}/DEBIAN/postinst
#!/bin/sh

# Check Python version
PYTHON_VERSION=\$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

REQUIRED_VERSION="3.9"

# Compare versions
if [ "\$(printf '%s\n' "\$REQUIRED_VERSION" "\$PYTHON_VERSION" | sort -V | head -n1)" != "\$REQUIRED_VERSION" ]; then
  echo "Python version must be 3.9 or higher. Current version: \$PYTHON_VERSION"
  exit 1
fi

python3 -m venv /opt/screenvivid/venv
. /opt/screenvivid/venv/bin/activate

pip install -q -r /opt/screenvivid/requirements.txt

ln -sf /opt/screenvivid/run /usr/bin/screenvivid

chmod +x /opt/screenvivid/run

exit 0
EOF

# Make postinst executable
chmod 755 ${PKG_NAME}-${VERSION}-${ARCH}/DEBIAN/postinst


# Create the .desktop file
cat << EOF > ${PKG_NAME}-${VERSION}-${ARCH}/usr/share/applications/${PKG_NAME}.desktop
[Desktop Entry]
Name=${DISPLAY_NAME}
Exec=/usr/bin/${PKG_NAME}
Icon=${PKG_NAME}
Type=Application
Categories=Utility;
Comment=Screen recording and editing application
EOF

# Copy the icon
cp ../../screenvivid/resources/icons/screenvivid.png ${PKG_NAME}-${VERSION}-${ARCH}/usr/share/icons/hicolor/256x256/apps/${PKG_NAME}.png

# Build the .deb package
dpkg-deb --build ${PKG_NAME}-${VERSION}-${ARCH}

# Clean up
rm -rf ${PKG_NAME}-${VERSION}-${ARCH}

echo "Debian package created: ${PKG_NAME}-${VERSION}-${ARCH}.deb"