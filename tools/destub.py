#!/usr/bin/env python3
#
import cm.read
import cm.write

import wc.data_update
from wc.config import config
import sys
import os
import yaml
import glob
import argparse
import readline
import datetime

def parse_cli():
  parser = argparse.ArgumentParser(description='Change English hike description from stub to full-blown hike')
  parser.add_argument('hike', nargs=1,action='store',help='Hike name')
  parser.add_argument('--now',dest='now',action='store_true')
  parser.add_argument('--template','-t',dest='template',action='store', \
    default="hikes-template.yaml", \
    help='Data template')
  return parser.parse_args()

def destub_hike(path,template,set_date):
  idx_path = f'{path}/index.en.md'
  page = cm.read.page(idx_path)
  for tk in template.keys():
    if not 'destub' in template[tk]:
      continue

    if tk in page:
      continue

    page[tk] = None
    if 'en' in template[tk]:
      page[tk] = template[tk]['en']

  page['layout'] = 'structured'
  if set_date:
    page['date'] = datetime.datetime.now(datetime.timezone.utc)

  if not page.get('markdown',None):
    page['markdown'] = '''
{{<hike-details description="yes">}}

## Notes

'''

  cm.write.create_output_file(data=page,target_path=path,name="index.en")

args = parse_cli()
template = wc.data_update.read_template(args.template,search_path=[os.path.dirname(__file__)])

hike_name = args.hike[0]

if not os.path.exists(hike_name):  
  print(f"Cannot find hike directory {hike_name}")
  sys.exit()

destub_hike(hike_name,template,args.now)
