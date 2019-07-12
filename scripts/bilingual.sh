#!/bin/sh

form=$(basename $1 | sed 's/_.*//')
output=$(echo $1 | sed 's/\.pdf/_bilingual\.pdf/')
pdftk A="$1" B=".upstream/$form.pdf" shuffle A B output "$output"
