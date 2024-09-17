#!/bin/bash

# Application name (lowercase for package name, mixed case for display name)
PKG_NAME="screenvivid"
DISPLAY_NAME="ScreenVivid"

# Version number
VERSION=${1:-"1.0.0"}

# Architecture
ARCH="amd64"

# Create directory structure for the .deb package
mkdir -p ${PKG_NAME}_${VERSION}_${ARCH}/DEBIAN
mkdir -p ${PKG_NAME}_${VERSION}_${ARCH}/opt/${PKG_NAME}
mkdir -p ${PKG_NAME}_${VERSION}_${ARCH}/usr/share/applications
mkdir -p ${PKG_NAME}_${VERSION}_${ARCH}/usr/share/icons/hicolor/256x256/apps
mkdir -p ${PKG_NAME}_${VERSION}_${ARCH}/usr/bin

# Create the control file
cat << EOF > ${PKG_NAME}_${VERSION}_${ARCH}/DEBIAN/control
Package: ${PKG_NAME}
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: Dark Photon <tamnvhustcc@gmail.com>
Description: Screen recording and editing application
 ${DISPLAY_NAME} is a cross-platform desktop application for screen recording
 and video editing, featuring options like background replacement and padding.
EOF

# Copy the entire application directory
cp -R dist/${DISPLAY_NAME}/* ${PKG_NAME}_${VERSION}_${ARCH}/opt/${PKG_NAME}/

# Create a soft link in /usr/bin
ln -s /opt/${PKG_NAME}/${DISPLAY_NAME} ${PKG_NAME}_${VERSION}_${ARCH}/usr/bin/${PKG_NAME}

# Create the .desktop file
cat << EOF > ${PKG_NAME}_${VERSION}_${ARCH}/usr/share/applications/${PKG_NAME}.desktop
[Desktop Entry]
Name=${DISPLAY_NAME}
Exec=/usr/bin/${PKG_NAME}
Icon=${PKG_NAME}
Type=Application
Categories=Utility;
EOF

# Copy the icon
cp ../../screenvivid/resources/icons/screenvivid.png ${PKG_NAME}_${VERSION}_${ARCH}/usr/share/icons/hicolor/256x256/apps/${PKG_NAME}.png

# Build the .deb package
dpkg-deb --build ${PKG_NAME}_${VERSION}_${ARCH}

# Clean up
rm -rf ${PKG_NAME}_${VERSION}_${ARCH}

echo "Debian package created: ${PKG_NAME}_${VERSION}_${ARCH}.deb"