#!/usr/bin/env python3
#
import cm.msaccess

from wc.config import config
import cm.read
import cm.write
import sys
import yaml
import argparse
import os
import glob

def parse_cli():
  parser = argparse.ArgumentParser(description='Update flower links')
  parser.add_argument('--count',dest='count',default=9999,type=int,action='store',help='Maximum number of hikes to import')
#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

def moveFile(hike_file):
  path = os.path.dirname(hike_file)
  fname = os.path.basename(hike_file)

  fname_c = fname.split('.',1)
  dest = path + "/" + fname_c[0] + "/index." +fname_c[1]
  print("Moving %s to %s" % (hike_file,dest))
  os.rename(hike_file,dest)
  return True

args = parse_cli()
count = args.count
print("Fixing at most %d files" % count)
path = config['ExFilePath']

for hike_file in glob.glob(path+'/*.md'):
  if hike_file.find("/_") >= 0:
    print("Index file"+hike_file)
    continue

  if moveFile(hike_file):
    count = count - 1
  if count <= 0:
    break
