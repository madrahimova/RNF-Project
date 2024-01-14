#!/usr/bin/env bash

VER="$1"
DATE="$(date -R)"
CHANGELOG_PATH="rnf-backend/DEBIAN/changelog"

if [ "$VER" == "" ]; then
  VER=0.1
fi

INPUT=`sed "s/VER/$VER/g; s/DATE/$DATE/g" changelog_tmpl`
echo -e "$INPUT\n\n$(cat $CHANGELOG_PATH)" > "$CHANGELOG_PATH"