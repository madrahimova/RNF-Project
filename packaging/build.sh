#!/usr/bin/env bash

set -e

sudo apt update
sudo apt install -y dpkg-dev devscripts python3 python3-pip python3-venv
python3 -m venv env
source env/bin/activate
python3 -m pip install -r ../requirements.txt

SRC_PATH="rnf-backend"

rm -rf "$SRC_PATH/spec" "$SRC_PATH/dist" "$SRC_PATH/build"
pyinstaller --specpath "$SRC_PATH/spec" --distpath "$SRC_PATH/dist" --workpath "$SRC_PATH/build" ../main.py -n api

CHANGELOG_PATH="$SRC_PATH/debian/changelog"
CHANGELOG="$(cat $CHANGELOG_PATH)"

if [ "$CHANGELOG" == "" ]; then
  . changelog_gen.sh
fi

cd "$SRC_PATH" && dpkg-buildpackage -us -uc -b