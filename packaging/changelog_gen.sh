#!/usr/bin/env bash

set -e

VER="$1"
DATE="$(date -R)"
CHANGELOG_PATH="rnf-backend/debian/changelog"

if [ "$VER" == "" ]; then
  VER=0.1
fi

INPUT=`sed "s/VER/$VER/g; s/DATE/$DATE/g" changelog_tmpl`
CHANGELOG="$(cat $CHANGELOG_PATH)"

if [ "$CHANGELOG" != "" ]; then
  INPUT="$INPUT\n\n"
fi

echo -e "$INPUT$(cat $CHANGELOG_PATH)" > "$CHANGELOG_PATH"