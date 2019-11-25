#!/usr/bin/env bash

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2
SHA1=$3

# Commitlint
if [ ! -d node_modules ]; then
  npm install @commitlint/cli@8.2.0 @commitlint/config-conventional@8.2.0
fi

# Lint last commit from history
./node_modules/.bin/commitlint --edit "$COMMIT_MSG_FILE"