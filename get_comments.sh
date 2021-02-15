#!/bin/bash

FOLDER=$(dirname "$0")

# python3 parser.py --output json | jq -r '.comments | to_entries | map([.key, .value]) | .[] | select(.[1] != "") | "'$(tput bold)'"+.[0]+"'$(tput sgr0)': "+.[1]'
python3 $FOLDER/parser.py --output json --remove-newlines | jq -r '.comments | to_entries | map([.key, .value]) | .[] | select(.[1] != "") | .[0]+": "+.[1]'
