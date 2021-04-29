#!/usr/bin/env python3
#
import cm.web
import cm.write
import wc.hike

from wc.config import config
import sys
import os
import yaml
import argparse
import wc.config
import cm.traverse
import cm.read
import cm.msaccess
import yaml

def parse_cli():
  parser = argparse.ArgumentParser(description='Sync SI/EN hike data')
  parser.add_argument('--precommit',dest='precommit',action='store_true',help='Running in pre-commit script, abort on error')
  return parser.parse_args()

def sync_hike_data(si_path):
  global errcount
  en_path = si_path.replace("index.md","index.en.md")
  if not os.path.exists(en_path):
    print("Missing stub file %s" % en_path)
    return

  si_page = cm.read.page(si_path)
  si_yaml = yaml.dump(si_page)
  en_page = cm.read.page(en_path)
  en_yaml = yaml.dump(en_page)

  for key in ('delta','duration','height','lead','multilead','multipath','maplink','start','peak','video','region'):
    si_val = si_page.get(key)
    en_val = en_page.get(key)
    if not si_val and not en_val:
      continue
    elif si_val and not en_val:
      en_page[key] = si_val
      print("Copying %s=%s from %s" % (key,si_val,si_path))
    elif not si_val and en_val:
      si_page[key] = en_val
      print("Copying %s=%s to %s" % (key,en_val,si_path))
    elif si_val != en_val:
      print("WARNING: SI/EN mismatch %s=(%s,%s) -- %s" % (key,si_val,en_val,si_path))
      if args.precommit:
        sys.exit(1)

  for key in ('x','y','image'):
    si_val = si_page.get(key)
    en_val = en_page.get(key)
    if en_val and not si_val:
      print("Removing property %s from %s" % (key,en_path))
      en_page.pop(key)

  for key in ['gpx']:
    if en_page.get(key,None):
      si_page[key] = en_page[key]

  if yaml.dump(si_page) != si_yaml:
    print("SI page changed, updating...")
    cm.write.create_output_file(si_page,file_path=si_path)
  if yaml.dump(en_page) != en_yaml:
    print("EN page changed, updating...")
    cm.write.create_output_file(en_page,file_path=en_path)

args = parse_cli()
cm.traverse.walk(config['ExFilePath'],r'index\.md$',sync_hike_data)
