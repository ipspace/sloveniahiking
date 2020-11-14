#
#
import cm.msaccess
import cm.web
import cm.cleanup
import cm.write
import wc.hike

from wc.config import config
import sys
import yaml
import argparse

def parse_cli():
  parser = argparse.ArgumentParser(description='Import hikes from Zaplana.net')
  parser.add_argument('hikes', nargs='*',action='store',help='Individual hikes to import')
  parser.add_argument('--count',dest='count',type=int,action='store',help='Maximum number of hikes to import')
  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

args = parse_cli()
config['force'] = args.force
ExTarget = cm.msaccess.read(config['ExTargetPath'])

for hike_row in ExTarget:
  if args.hikes and not hike_row['ExDirectory'] in args.hikes:
    continue

  if not wc.hike.fetch_hike(hike_row,config):
    continue

  if args.count:
    args.count = args.count - 1
    if args.count <= 0:
      break
