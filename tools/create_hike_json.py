#!/usr/bin/env python3
#
from wc.config import config
import sys
import os
import yaml
import argparse
import cm.traverse
import cm.read
import json

hike_json = []

def parse_cli():
  parser = argparse.ArgumentParser(description='Create Hike JSON data')
  parser.add_argument('--output',dest='output',default='../static/data/hikes.json',action='store',help='Output JSON file')
  return parser.parse_args()

def collect_hike_data(si_path):
  si_page = cm.read.page(si_path)

  for key in ('html','markdown','image'):
    si_page.pop(key,None)
  
  for key in list(si_page.keys()):
    if si_page[key] is None:
      si_page.pop(key)

  for key in ('date','lastmod'):
    if key in si_page:
      si_page[key] = str(si_page[key])

  for key in ('start','peak'):
    if key in si_page:
      si_page[key] = str(si_page[key]).replace(" ","")

  si_page['title'] = { 'sl': si_page.get('title') }
  si_page['description'] = { 'sl': si_page.get('description') }

  en_path = si_path.replace("index.md","index.en.md")
  if os.path.exists(en_path):
    en_page = cm.read.page(en_path)
    for lang_key in ('title','description'):
      si_page[lang_key]['en'] = en_page.get(lang_key)

  hike_json.append(si_page)

args = parse_cli()
cm.traverse.walk(config['ExFilePath'],r'index\.md$',collect_hike_data)
with open(args.output,"w") as output_file:
  json.dump(hike_json,fp=output_file,indent=2)
  print("Created JSON file %s" % args.output)
  output_file.close()
