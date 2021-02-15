#
#
import cm.msaccess

from wc.config import config
from wc.flower import flowerFilePath
import cm.read
import cm.write
import sys
import yaml
import argparse
import os

def parse_cli():
  parser = argparse.ArgumentParser(description='Update flower links')
  parser.add_argument('--count',dest='count',default=9999,type=int,action='store',help='Maximum number of hikes to import')
#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

def extractLink(md):
  link = ""
  while md.find('(') >= 0 and md.find('(') < md.find(')'):
    (partial,md) = md.split('(',1)
    link = link + partial + '('
    (partial,md) = md.split(')',1)
    link = link + partial + ')'
  
  partial = md.split(')',1)
  link = link + partial[0]
  return (link,partial[1])

def lookupLink(link):
  if not "../" in link:
    return link

  link = link.replace("../../","../")
  if "family" in link or "genus" in link:
    return link

  suffix = ""
  if link.rfind("/") == len(link) - 1:
    link = os.path.dirname(link)
    suffix = "/"

  return os.path.dirname(link) + suffix

def replaceLinks(md):
  result = ""
  while md.find('](') > 0:
    tlist = md.split('](',1)
    result = result + tlist[0]
    md = tlist[1]
    (link,md) = extractLink(md)
    link = lookupLink(link)
    result = result + '](' + link + ')'

  return result + md

def updateLinks(flower):
  path = flowerFilePath(flower,config)
  page = cm.read.page(path+'/index.md')
  md = page.get('markdown','')
  page.pop('name',None)
  if md.find('](') < 0:
    return

  try:
    result = replaceLinks(md)
  except:
    print("Failed to update links in %s\n%s" % (path,str(sys.exc_info()[1])))
    return

  if result != md:
    page['markdown'] = result
    print("Updating %s" % path)
    cm.write.create_output_file(page,path)
    return True

args = parse_cli()
count = args.count
print("Fixing at most %d files" % count)
flower_data = cm.msaccess.read(config['ExFlowersPath'])

for flower in flower_data:
  if updateLinks(flower):
    count = count - 1
  if count <= 0:
    break
