#!/usr/bin/env python3
#

import sys
import os
import argparse

from wc.config import config
import cm.traverse
import cm.read
import cm.write

import geopy.distance

trips = []
updated_trips = []
pages = {}

def get_coords(fname):
  page = cm.read.page(fname)
  if not page:
    return

  if 'multipath' in page:
    latlon = page.get('start',None)
  else:
    latlon = page.get('peak',None)
    if not latlon:
      if 'gpx' in page:
        latlon = page['gpx'].get('center',None)
  if not latlon or 'startpoint' in page:
    return

  if isinstance(latlon,str):
    coords = latlon.split(',')
    latlon = { 'lat': float(coords[0]), 'lon': float(coords[1]) }

  pages[fname] = page
  trips.append({
    'path': fname,
    'nearby': page.get('nearby'),
    'multipath': page.get('multipath'),
    'name': page.get('name'),
    'type': 'biking' if 'biking' in fname else 'hikes',
    'coords': latlon
  })

def find_nearby_trips(t,trips):
  candidates = filter(lambda c: 
                        abs(t['coords']['lat'] - c['coords']['lat']) < 0.15 and 
                        abs(t['coords']['lon'] - c['coords']['lon']) < 0.07 and
                        c['name'] != t['name'] and not c.get('multipath'),
                      trips)
  sort_nearby = sorted(candidates,
                       key=lambda c:
                         geopy.distance.distance(
                           (c['coords']['lat'],c['coords']['lon']),
                           (t['coords']['lat'],t['coords']['lon'])))
  return list(map(lambda c: 
                    '/%s/%s' % (c['type'],c['name'].lower()),
                  list(sort_nearby)[0:5]))

def compute_nearby(trips):
  for t in trips:
    nearby = find_nearby_trips(t,trips)
    page = pages[t['path']]
    if nearby != page.get('nearby',None):
      page['nearby'] = nearby
      page['updated'] = True

def dump_modified(pages):
  for path,page in pages.items():
    if not page.get('updated',None):
      continue
    page.pop('updated',None)
    cm.write.create_output_file(data=page,file_path=path)

def parse_cli():
  parser = argparse.ArgumentParser(description='Get nearby trips')
  parser.add_argument('-v','--verbose',dest='verbose',action='store_true',help='Verbose printouts')
  return parser.parse_args()

args = parse_cli()

cm.traverse.walk(config['ExFilePath'],r'index\.md$',get_coords)
cm.traverse.walk(config['BikeFilePath'],r'index.*\.md$',get_coords)

compute_nearby(trips)
dump_modified(pages)