#!/bin/bash
me=${BASH_SOURCE:-$_}
echo "me: $me"
dir=$(dirname "$me")
dir=$(cd "$dir" >/dev/null && pwd)
echo Adding $dir to PATH
top=$(dirname $dir)
alias hikes="cd $top/content/hikes"
alias posts="cd $top/content/posts"
alias biking="cd $top/content/biking"
alias climbing="cd $top/content/climbing"
alias flowers="cd $top/content/flowers"
PATH=$dir:$PATH
