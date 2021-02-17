#!/bin/bash
dir=$(dirname "${BASH_SOURCE[0]}")
dir=$(cd "$dir" >/dev/null && pwd)
echo Adding $dir to PATH
PATH=$dir:$PATH
