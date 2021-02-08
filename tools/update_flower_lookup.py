#
#
import cm.msaccess

from wc.config import config
import sys
import yaml
import argparse

def parse_cli():
  parser = argparse.ArgumentParser(description='Import flowers lookup data from Zaplana.net')
#  parser.add_argument('--count',dest='count',type=int,action='store',help='Maximum number of hikes to import')
#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

args = parse_cli()
result = { 'family': {}, 'genus': {} }
for family in cm.msaccess.read(config['ExFlowersFamilyPath']):
  value = str(family['SloveneFamily'])
  result['family'][family['LatinFamily']] = value.capitalize()

for genus in cm.msaccess.read(config['ExFlowersGenusPath']):
  if genus.get('GenusSlovenianName',None):
    result['genus'][genus['BotanyGenus']] = genus['GenusSlovenianName'].capitalize()

with open(config['DataPath'] % "botany.yml","w") as output:
  output.write(yaml.dump(result))
  output.close