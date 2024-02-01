#!/bin/bash

set -e

apt update
apt install -y dpkg-dev devscripts debhelper python3 python3-pip python3-venv

SRC_PATH="rnf-backend"
CHANGELOG_PATH="$SRC_PATH/debian/changelog"
CHANGELOG="$(cat $CHANGELOG_PATH)"

if [ "$CHANGELOG" == "" ]; then
  . changelog_gen.sh "$VER"
fi

cd "$SRC_PATH"
dch -v "$VER" "all latest updates"
dpkg-buildpackage -b -uc -us
rm -rf api.spec build dist
dh_clean
cd ..