#!/usr/bin/env python3
#

import sys
import os
import argparse
import datetime

from wc.config import config
import cm.traverse
import cm.read
import cm.write

import geopy.distance

trips = []
updated_trips = []
pages = {}

def get_page_latlon(page):
  if 'multipath' in page:
    latlon = page.get('start',None)
  else:
    latlon = page.get('peak',None)
    if not latlon:
      if 'gpx' in page:
        latlon = page['gpx'].get('center',None)

  if isinstance(latlon,str):
    coords = latlon.split(',')
    latlon = { 'lat': float(coords[0]), 'lon': float(coords[1]) }

  return latlon

def get_coords(fname):
  page = cm.read.page(fname)
  if not page:
    return

  if 'date' in page and page['date'] > datetime.datetime.now(datetime.timezone.utc):
    print(f"Skipping {fname} -- published on {str(page['date'])}")
    return

  latlon = get_page_latlon(page)
  if not latlon:
    return

  pages[fname] = page
  trips.append({
    'path': fname,
    'nearby': page.get('nearby'),
    'multipath': page.get('multipath'),
    'name': page.get('name'),
    'type': 'biking' if 'biking' in fname else 'hikes',
    'coords': latlon
  })

def read_page(fname):
  page = cm.read.page(fname)
  if not page:
    return

  pages[fname] = page

def find_nearby_trips(t,trips,radius,include):
  candidates = filter(lambda c:
                        abs(t['coords']['lat'] - c['coords']['lat']) < radius and
                        abs(t['coords']['lon'] - c['coords']['lon']) < radius * 1.4 and
                        c['name'] != t['name'] and not c.get('multipath') and c['type'] in include,
                      trips)
  sort_nearby = sorted(candidates,
                       key=lambda c:
                         geopy.distance.distance(
                           (c['coords']['lat'],c['coords']['lon']),
                           (t['coords']['lat'],t['coords']['lon'])))
  selection = list(map(lambda c:
                    '/%s/%s' % (c['type'],c['name'].lower()),
                  list(sort_nearby)[0:5]))
  return selection

def compute_nearby(pages):
  for path,page in pages.items():
    latlon = get_page_latlon(page)
    if not latlon:
      continue
    t = {
      'path': path,
      'name': page.get('name'),
      'coords': latlon
    }
    include = ['hikes','biking'] if '.en.md' in path else ['hikes']
    nearby = find_nearby_trips(t,trips,0.15,include)
    if len(nearby) < 3:
      nearby = find_nearby_trips(t,trips,0.3,include)
    if nearby != page.get('nearby',None):
      page['nearby'] = nearby
      page['updated'] = True

def dump_modified(pages,dry_run):
  for path,page in pages.items():
    if not page.get('updated',None):
      continue
    page.pop('updated',None)
    if dry_run:
      print(f"{path}: {page.get('nearby',None)}")
      continue
    else:
      cm.write.create_output_file(data=page,file_path=path)

def parse_cli():
  parser = argparse.ArgumentParser(description='Get nearby trips')
  parser.add_argument('-v','--verbose',dest='verbose',action='store_true',help='Verbose printouts')
  parser.add_argument('--dry',dest='dry',action='store_true',help='Dry run')
  return parser.parse_args()

args = parse_cli()

cm.traverse.walk(config['ExFilePath'],r'index\.en\.md$',get_coords)
cm.traverse.walk(config['ExFilePath'],r'index\.md$',read_page)
cm.traverse.walk(config['BikeFilePath'],r'index.*\.md$',get_coords)

compute_nearby(pages)
dump_modified(pages,args.dry)