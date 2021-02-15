#!/bin/bash
FZF_DEFAULT_COMMAND=./get_comments.sh fzf --preview './kbdisplay.py "$(echo {} | cut -d: -f1)"; echo {} | '"sed -e 's/\. /\'$'\n/g'" --preview-window=down:20
