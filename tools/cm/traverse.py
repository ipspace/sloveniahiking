#
# Traverse a directory looking for files matching a pattern
# Execute a callback on every file found

import re
import os

def yell(p):
  print("Found %s" % p)

def walk(path=None,pattern=None,callback=yell):
  with os.scandir(path) as dir:
    for entry in dir:
      if entry.is_dir():
        if not entry.name.startswith('.'):
          walk(os.path.join(path,entry.name),pattern,callback)
      elif entry.is_file():
        if re.search(pattern,entry.name):
          callback(os.path.join(path,entry.name))
