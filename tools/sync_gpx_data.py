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
import cm.gpx

def parse_cli():
  parser = argparse.ArgumentParser(description='Sync SI/EN hike data')
  parser.add_argument('--precommit',dest='precommit',action='store_true',help='Running in pre-commit script, abort on error')
  parser.add_argument('-v','--verbose',dest='verbose',action='store_true',help='Verbose printouts')
  return parser.parse_args()

args = parse_cli()
cm.gpx.VERBOSE=args.verbose

cm.traverse.walk(config['ExFilePath'],r'\.gpx$',cm.gpx.sync_gpx_data)
cm.traverse.walk(config['BikeFilePath'],r'\.gpx$',cm.gpx.sync_gpx_data)
