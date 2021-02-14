#!/usr/bin/env python3
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
  parser.add_argument('--count',dest='count',default=9999,type=int,action='store',help='Maximum number of hikes to import')
#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

def fix_caption(match):
#  print("L: %s M: %s R: %s" % (match.group(1),match.group(2),match.group(3)))
  original = match.group(0)
  text = match.group(2)
#  print("text to work with: %s" % text)
  if "caption-position" in text:
    return original
  if 'src="M' in text:
    return original
  if 'razgled' in text.lower() or 'pogled' in text.lower():
    return match.group(1) + text + ' caption-position="bottom"' + match.group(3)
  return original

def update_captions(hike_file):
#  print("Hike_File: %s" % hike_file)
  page = cm.read.page(hike_file)
  md = page.get('markdown',None)

  if not md:
    return False

  md = re.sub('({{<figure)(.*?)(>}})',fix_caption,md)
  if md != page.get('markdown'):
    page['markdown'] = md
    print("Updating: "+hike_file)
    cm.write.create_output_file(page,os.path.dirname(hike_file),os.path.basename(hike_file).replace(".md",""))
    args.count = args.count - 1
    if args.count <= 0:
      print("Enough, exiting...")
      sys.exit(0)
    return True

  return False

args = parse_cli()
count = args.count
print("Fixing at most %d files" % count)

cm.traverse.walk(path=config['ExFilePath'],pattern='_?index\.(en\.)?md',callback=update_captions)
