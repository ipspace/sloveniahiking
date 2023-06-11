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
import hike.common
import yaml

def parse_cli():
  parser = argparse.ArgumentParser(description='Sync SI/EN hike data')
  parser.add_argument('--precommit',dest='precommit',action='store_true',help='Running in pre-commit script, abort on error')
  return parser.parse_args()

def sync_pages(en_page: dict, en_path: str, si_page: dict, si_path: str) -> None:
  for key in ['delta','duration','height','difflevel',
              'lead','multilead','multipath',
              'maplink','start','startpoint','peak','icon',
              'video','region']:
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

  for key in ['x','y','image']:
    si_val = si_page.get(key)
    en_val = en_page.get(key)
    if en_val and not si_val:
      print("Removing property %s from %s" % (key,en_path))
      en_page.pop(key)

  for key in ['name']:
    if key in si_page:
      en_page[key] = si_page[key]

  for key in ['nearby']:
    if si_page.get(key,None):
      if not en_page.get(key,None):
        en_page[key] = si_page[key]
        print("Copying %s from %s" % (key,si_path))

  if 'gpx' in en_page and not 'map' in si_page:
    si_page['gpx'] = en_page['gpx']

def sync_hike_data(en_path):
  global errcount

  en_page = cm.read.page(en_path)
  en_yaml = yaml.dump(en_page)

  si_path = en_path.replace("index.en.md","index.md")
  if not os.path.exists(si_path):
#    print("Missing stub file %s" % si_path)
    si_page = None
    si_yaml = None
  else:
    si_page = cm.read.page(si_path)
    si_yaml = yaml.dump(si_page)

  if 'nosync' in en_page:
    print(f"Skipping {en_path} due to 'nosync' parameter")
    return

  hike.common.cleanup(en_page)
  hike.common.set_hike_difflevel(en_page)
  if not 'difflevel' in en_page:
    hike.common.set_icon(en_page)

  if si_page:
    hike.common.cleanup(si_page)
    sync_pages(en_page,en_page,si_page,si_path)
    if yaml.dump(si_page) != si_yaml:
      print("SI page changed, updating...")
      cm.write.create_output_file(si_page,file_path=si_path)

  if yaml.dump(en_page) != en_yaml:
    print("EN page changed, updating...")
    cm.write.create_output_file(en_page,file_path=en_path)

args = parse_cli()
cm.traverse.walk(config['ExFilePath'],r'index\.en\.md$',sync_hike_data)
