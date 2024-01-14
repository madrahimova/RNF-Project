#!/usr/bin/env bash

SRC_PATH="rnf-backend"

. changelog_gen.sh
python3 -m pip install -r requirements.txt
