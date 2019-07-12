#!/bin/sh
ls *_bilingual.pdf | while read f; do mv "$f" "$(echo $f | sed 's/_bilingual//')"; done
