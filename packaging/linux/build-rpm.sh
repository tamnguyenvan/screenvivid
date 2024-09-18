#!/bin/bash

# Set variables
PKG_NAME="screenvivid"
APP_NAME="ScreenVivid"
VERSION=${1:-"1.0.0"}
RELEASE="1"
SOURCE_DIR="dist/${APP_NAME}"
RPM_DIR="/tmp/${APP_NAME}-rpm"
SPEC_FILE="${APP_NAME}.spec"
TARBALL="${APP_NAME}-${VERSION}.tar.gz"

# Create directories for RPM
mkdir -p "${RPM_DIR}/BUILD" "${RPM_DIR}/RPMS" "${RPM_DIR}/SOURCES" "${RPM_DIR}/SPECS" "${RPM_DIR}/SRPMS"

# Create a temporary directory for the tarball
TEMP_DIR="${RPM_DIR}/SOURCES/${APP_NAME}-${VERSION}"
mkdir -p "${TEMP_DIR}"

# Copy the executable and _internal directory to the temporary directory
cp -r "${SOURCE_DIR}/ScreenVivid" "${TEMP_DIR}/"
cp -r "${SOURCE_DIR}/_internal" "${TEMP_DIR}/"

# Create a tarball of the application
tar -czf "${RPM_DIR}/SOURCES/${TARBALL}" -C "${RPM_DIR}/SOURCES" "${APP_NAME}-${VERSION}"

# Create the SPEC file
cat <<EOL > "${RPM_DIR}/SPECS/${SPEC_FILE}"
%global debug_package %{nil}

Name: ${PKG_NAME}
Version: ${VERSION}
Release: ${RELEASE}
Summary: A cross-platform screen recording and editing application
License: MIT
Group: Applications/Multimedia
Source: ${TARBALL}
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
${APP_NAME} is a cross-platform desktop application for screen recording and video editing.

%prep
%setup -q -n ${APP_NAME}-${VERSION}

%build

%install
mkdir -p %{buildroot}/opt/${PKG_NAME}
cp ScreenVivid %{buildroot}/opt/${PKG_NAME}/  # Copy the executable
cp -r _internal %{buildroot}/opt/${PKG_NAME}/  # Copy the _internal directory

# Create symlink
mkdir -p %{buildroot}/usr/bin
ln -s /opt/${PKG_NAME}/ScreenVivid %{buildroot}/usr/bin/${PKG_NAME}

%files
/opt/${PKG_NAME}
/usr/bin/${PKG_NAME}

%changelog
* $(date +"%a %b %d %Y") Dark Photon <tamnvhustcc@gmail.com> - ${VERSION}-${RELEASE}
- Initial RPM release
EOL

# Build the .rpm file
rpmbuild --define "_topdir ${RPM_DIR}" -ba "${RPM_DIR}/SPECS/${SPEC_FILE}"

# Move the .rpm file to the current directory and rename it
mv "${RPM_DIR}/RPMS/x86_64/${PKG_NAME}-${VERSION}-${RELEASE}.x86_64.rpm" "${PKG_NAME}-${VERSION}.x86_64.rpm"

# Clean up temporary files
rm -rf "${RPM_DIR}"

echo "RPM package created: ${PKG_NAME}-${VERSION}.x86_64.rpm"