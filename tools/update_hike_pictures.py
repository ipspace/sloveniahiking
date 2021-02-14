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

def parse_cli():
  parser = argparse.ArgumentParser(description='Update hike pictures')
  parser.add_argument('hikes', nargs='*',action='store',help='Individual hikes to fix')
  parser.add_argument('--lookup',dest='lookup',default='../xfer/hike-picture-lookup.yml', \
    action='store',help='Lookup YAML file')
  parser.add_argument('-v',dest='verbose',action='store_true',help='Verbose printout')
  parser.add_argument('-q',dest='quiet',action='store_true',help='Be as quiet as possible')

#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

args = parse_cli()

with open(args.lookup,"r") as lookup_file:
  lookup = yaml.safe_load(lookup_file)

if args.hikes:
  for hike_name in args.hikes:
    path = config['ExFilePath']+"/"+hike_name
    print("Updating pictures in %s" % path)
    cm.traverse.walk(path=path,pattern='(?i)\.jpg',callback=lambda p: cm.images.replace_image(p,lookup))
else:
  cm.traverse.walk(path=config['ExFilePath'],pattern='(?i)\.jpg',callback=lambda p: cm.images.replace_image(p,lookup))