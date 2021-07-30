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

difflevel_limits = {
  1 : { 'length': 30, 'duration' : 3, 'incline' : 2 },
  2 : { 'incline': 6, 'delta': 600 },
  3 : { 'incline': 99 }
}

def update_biking_data(path):
  global errcount

  page = cm.read.page(path)
  y_before = yaml.dump(page)

  hike.common.cleanup(page)
  if 'length' in page and 'delta' in page:
    page['incline'] = page['delta'] / page['length'] / 5
    hike.common.set_hike_difflevel(page,difflevel_limits)

  page.pop('incline',None)
  if yaml.dump(page) != y_before:
    print("Biking page changed, updating...")
    cm.write.create_output_file(page,file_path=path)

args = parse_cli()
cm.traverse.walk(config['BikeFilePath'],r'index\.en\.md$',update_biking_data)
