#!/bin/sh
git diff --no-ext-diff --quiet --exit-code "$1" && \
date=$(git log --pretty='%aD' -n 1 -- "$1") && \
# echo "restoring mtime of $1 to $date" && \
touch -md "$date" "$1"
