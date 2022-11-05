#
#
import cm.msaccess
import cm.web
import cm.cleanup
import cm.write
import wc.flower

from wc.config import config
import sys
import yaml
import argparse

def parse_cli():
  parser = argparse.ArgumentParser(description='Import flowers from Zaplana.net')
  parser.add_argument('flowers', nargs='*',action='store',help='Individual flowers to import')
  parser.add_argument('--count',dest='count',type=int,action='store',help='Maximum number of hikes to import')
  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

args = parse_cli()
config['force'] = args.force
ExFlowers = cm.msaccess.read(config['ExFlowersPath'])

for flowers_row in ExFlowers:
#  if args.hikes and not hike_row['ExDirectory'] in args.hikes:
#    continue

  fdata = wc.flower.fetch_flower(flowers_row,config)
  if fdata:
    wc.flower.write_en_stub(flowers_row,fdata,config)

  if args.count:
    args.count = args.count - 1
    if args.count <= 0:
      break
