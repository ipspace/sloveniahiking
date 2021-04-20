#!/bin/bash
dir=$(dirname "${BASH_SOURCE[0]}")
dir=$(cd "$dir" >/dev/null && pwd)
echo Adding $dir to PATH
top=$(dirname $dir)
alias hikes="cd $top/content/hikes"
alias posts="cd $top/content/posts"
alias biking="cd $top/content/biking"
alias flowers="cd $top/content/flowers"
PATH=$dir:$PATH
