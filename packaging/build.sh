#!/bin/bash

set -e

sudo apt update
sudo apt install -y dpkg-dev devscripts python3 python3-pip python3-venv

SRC_PATH="rnf-backend"
CHANGELOG_PATH="$SRC_PATH/debian/changelog"
CHANGELOG="$(cat $CHANGELOG_PATH)"

if [ "$CHANGELOG" == "" ]; then
  . changelog_gen.
fi

cd "$SRC_PATH" && dpkg-buildpackage -b -uc -us
rm -rf api.spec build dist
dh_clean