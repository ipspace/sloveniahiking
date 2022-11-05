#/usr/bin/env python3
#
import cm.msaccess

from wc.config import config
import sys
import yaml
import argparse
import os
import glob
import re
import shutil
import cm.traverse
import cm.images
import cm.read

def parse_cli():
  parser = argparse.ArgumentParser(description='Update flower pictures')
  parser.add_argument('--lookup',dest='lookup',default='../xfer/flower-picture-lookup.yml', \
    action='store',help='Lookup YAML file')
  parser.add_argument('-v',dest='verbose',action='store_true',help='Verbose printout')
  parser.add_argument('-q',dest='quiet',action='store_true',help='Be as quiet as possible')

#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

def flower_author(p):
  idx = os.path.dirname(p)+"/index.md"
  page = cm.read.page(idx)
  if page:
    author = page.get("author")
    if author:
      author = author.replace("_"," ")
      print("author for %s: %s" % (p,author))
      return "© "+author

  return None

args = parse_cli()

with open(args.lookup,"r") as lookup_file:
  lookup = yaml.safe_load(lookup_file)

cm.traverse.walk(path=config['FlowersContent'],pattern='(?i)\.jpg', \
   callback=lambda p: \
     cm.images.replace_image(p,lookup=lookup,do_watermark=True,author=flower_author))