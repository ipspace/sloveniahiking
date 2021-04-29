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
import gpxpy
import gpxpy.gpx
import statistics

def parse_cli():
  parser = argparse.ArgumentParser(description='Sync SI/EN hike data')
  parser.add_argument('--precommit',dest='precommit',action='store_true',help='Running in pre-commit script, abort on error')
  parser.add_argument('-v','--verbose',dest='verbose',action='store_true',help='Verbose printouts')
  return parser.parse_args()

errcount = 0
VERBOSE=False

def get_gpx_info(gpx_path):
  with open(gpx_path,'r') as gpxfile:
    gpx = gpxpy.parse(gpxfile)
    gpxfile.close()

  points = []
  for t in gpx.tracks:
    for s in t.segments:
      points.extend(list(s.points))

  lat_list = list(map(lambda x: x.latitude, points))
  lon_list = list(map(lambda x: x.longitude, points))

  info = {}
  info['min_lat'] = min(lat_list)
  info['min_lon'] = min(lon_list)
  info['max_lat'] = max(lat_list)
  info['max_lon'] = max(lon_list)
  info['center_lat'] = (info['min_lat']+info['max_lat'])/2
  info['center_lon'] = (info['min_lon']+info['max_lon'])/2
  info['delta_lat'] = (info['max_lat']-info['min_lat'])
  info['delta_lon'] = (info['max_lon']-info['min_lon'])
  return info

def sync_gpx_data(gpx_path):
  global errcount

  if VERBOSE:
    print("Found GPX file %s" % gpx_path)

  content_dir = os.path.dirname(gpx_path)
  index_name = None

  for idx_name in ('index.en.md','_index.en.md','index.md','_index.md'):
    if os.path.exists(content_dir+"/"+idx_name):
      index_name = content_dir+"/"+idx_name
      break

  if not index_name:
    print("Cannot find index file in %s" % content_dir)
    return

  page = cm.read.page(index_name)
  page_dump = yaml.dump(page)

  if not 'gpx' in page:
    page['gpx'] = {}
  else:
    if page['gpx'].get('modified',None) == os.path.getmtime(gpx_path):
      if VERBOSE:
        print("GPX timestamp match, exiting")
##      return

  page['gpx']['file'] = os.path.basename(gpx_path)
  page['gpx']['modified'] = os.path.getmtime(gpx_path)
  
  gpx_info = get_gpx_info(gpx_path)
  page['gpx']['center'] = { 'lat': gpx_info['center_lat'], 'lon': gpx_info['center_lon']}

  if gpx_info['delta_lat'] < 0.0202 and gpx_info['delta_lon'] < 0.0483:
    page['gpx']['zoom'] = 14

  if gpx_info['delta_lat'] < 0.0100 and gpx_info['delta_lon'] < 0.0240:
    page['gpx']['zoom'] = 15

##  print("%s - %.6f %.6f" % (index_name,gpx_info['delta_lat'],gpx_info['delta_lon']))

  if yaml.dump(page) != page_dump:
    print("Page changed based on information in %s, updating..." % gpx_path)
    cm.write.create_output_file(page,file_path=index_name)

args = parse_cli()
VERBOSE=args.verbose

cm.traverse.walk(config['ExFilePath'],r'\.gpx$',sync_gpx_data)
cm.traverse.walk(config['BikeFilePath'],r'\.gpx$',sync_gpx_data)
