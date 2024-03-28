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

def sync_flower_data(path):
  si_page = cm.read.page(path)
  en_path = path.replace("index.md","index.en.md")
  if not os.path.exists(en_path):
    print(f"Cannot find {en_path}")
    return

  en_page = cm.read.page(en_path)
  en_yaml = yaml.dump(en_page)

  for k in si_page.keys():
    if k in ['title','layout','html','markdown','name']:
      continue

    if k not in en_page:
      print(f'{k} missing in {en_path}')
      en_page[k] = si_page[k]
      continue

    if en_page[k] != si_page[k]:
      print(f'{k} changed to {si_page[k]} in {en_path}')
      en_page[k] = si_page[k]

  if yaml.dump(en_page) != en_yaml:
    print(f"EN page {en_path} changed, updating...")
    cm.write.create_output_file(en_page,file_path=en_path)

cm.traverse.walk(config['FlowersContent'],r'index.md$',sync_flower_data)
