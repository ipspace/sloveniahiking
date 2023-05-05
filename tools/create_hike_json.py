#!/usr/bin/env python3
#
from wc.config import config
import sys
import os
import yaml
import argparse
import datetime
import cm.traverse
import cm.read
import json

hike_json = []

def parse_cli():
  parser = argparse.ArgumentParser(description='Create Hike JSON data')
  parser.add_argument('--output',dest='output',default='../static/data/hikes.json',action='store',help='Output JSON file')
  return parser.parse_args()

def process_page(page,lang):
  for key in ('html','markdown','image'):
    page.pop(key,None)
  
  for key in list(page.keys()):
    if page[key] is None:
      page.pop(key)

  for key in ('date','lastmod'):
    if key in page:
      page[key] = str(page[key])

  for key in ('start','peak'):
    if key in page:
      page[key] = str(page[key]).replace(" ","")

  page['title'] = { lang: page.get('title') }
  page['description'] = { lang: page.get('description') }

def collect_hike_data(page_path):
  global hike_json

  is_english = '.en.' in page_path
  hike_page = cm.read.page(page_path)
  if not 'name' in hike_page:
    return

  ck_name = os.path.dirname(page_path).replace('../content/hikes/','')
  if ck_name != hike_page['name']:
    print(f"{page_path}: {ck_name} != {hike_page['name']}")

  if 'date' in hike_page and hike_page['date'] > datetime.datetime.now(datetime.timezone.utc):
    print(f"Skipping {page_path} -- published on {str(hike_page['date'])}")
    return

  for key in ('html','markdown','image'):
    hike_page.pop(key,None)
  
  for key in list(hike_page.keys()):
    if hike_page[key] is None:
      hike_page.pop(key)

  for key in ('date','lastmod'):
    if key in hike_page:
      hike_page[key] = str(hike_page[key])

  for key in ('start','peak'):
    if key in hike_page:
      hike_page[key] = str(hike_page[key]).replace(" ","")

  lang = 'en' if is_english else 'sl'

  add_idx = None
  for idx,page in enumerate(hike_json):
    if page['name'] == hike_page['name'] and not 'type' in page:
      add_idx = idx

  if not add_idx is None:
    for lang_key in ('title','description'):
      if lang_key in hike_page:
        hike_json[add_idx][lang_key][lang] = hike_page.get(lang_key)
  else:
    hike_page['title'] = { lang: hike_page.get('title') }
    hike_page['description'] = { lang: hike_page.get('description') }
    hike_json.append(hike_page)

def collect_bike_data(index_path):
  global hike_json

  page = cm.read.page(index_path)
  if 'date' in page and page['date'] > datetime.datetime.now(datetime.timezone.utc):
    print(f"Skipping {index_path} -- published on {str(page['date'])}")
    return

  process_page(page,'en')
  page['type'] = 'biking'

  if 'gpx' in page:
    for key in ('start'):
      page.pop(key,None)
    page['center'] = format("%.6f,%.6f" % (page['gpx']['center']['lat'],page['gpx']['center']['lon']))
    page.pop('gpx')

  hike_json.append(page)

args = parse_cli()
cm.traverse.walk(config['ExFilePath'],r'index\.md$',collect_hike_data)
cm.traverse.walk(config['ExFilePath'],r'index\.en\.md$',collect_hike_data)
cm.traverse.walk(config['BikeFilePath'],r'index\.en\.md$',collect_bike_data)
with open(args.output,"w") as output_file:
  json.dump(hike_json,fp=output_file,indent=2)
  print("Created JSON file %s" % args.output)
  output_file.close()
