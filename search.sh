#!/bin/bash

FOLDER=$(dirname "$0")
FZF_DEFAULT_COMMAND=$FOLDER/get_comments.sh fzf --preview $FOLDER'/kbdisplay.py "$(echo {} | cut -d: -f1)"; echo {} | '"sed -e 's/\. /\'$'\n/g'" --preview-window=down:20
