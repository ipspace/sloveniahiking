#!/usr/bin/env python3
#
# Start from 'tools' directory with
# PYTHONPATH=. python3 fix/update_flower_metadata.py
#
from wc.config import config
import cm.read
import cm.write
import sys
import yaml
import argparse
import os
import glob
import re
import cm.traverse

def parse_cli():
  parser = argparse.ArgumentParser(description='Update flower links')
  parser.add_argument('--count',dest='count',default=2,type=int,action='store',help='Maximum number of hikes to import')
#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

def update_metadata(md_file):
  page = cm.read.page(md_file)
  yml_old = yaml.dump(page,allow_unicode=True)

  # Convert numbers from strings to ints
  #
  for k in page.keys():
    if isinstance(page[k],bool):
      continue
    try:
      v = int(page[k])
      page[k] = v
    except:
      pass

  yml_new = yaml.dump(page,allow_unicode=True)
  if yml_old == yml_new:
    return

  print("Updating: "+md_file)
  cm.write.create_output_file(page,file_path=md_file)
  args.count = args.count - 1
  if args.count <= 0:
    print("Enough, exiting...")
    sys.exit(0)

args = parse_cli()
count = args.count
print("Fixing at most %d files" % count)

print("Fixing Slovenian pages")
cm.traverse.walk(path=config['FlowersContent'],pattern='_?index\.md',callback=update_metadata)
print("Fixing English pages")
cm.traverse.walk(path=config['FlowersContent'],pattern='_?index.en.md',callback=update_metadata)
