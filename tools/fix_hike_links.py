#
#
import cm.msaccess

from wc.config import config
from wc.hike import get_target_directory
import cm.read
import cm.write
import sys
import yaml
import argparse
import os
import glob

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
  if link.find('http') == 0:
    if link.find('zaplana') > 0:
      raise Exception("External link to zaplana.net: %s" % link)
    return link

  if link.find('/images/') > 0:
    raise Exception("Link to /images: %s" % link)

  return link.lower()

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

def update_hike_links(idx_file,hike):
  page = cm.read.page(idx_file)
  md = page.get('markdown','')
  if md.find('](') < 0:
    return

  try:
    result = replaceLinks(md)
  except:
    print("Failed to update links in %s\n%s" % (idx_file,str(sys.exc_info()[1])))
    sys.exit(1)
    return

  if result != md:
    page['markdown'] = result
    path = os.path.dirname(idx_file)
    name = os.path.basename(idx_file).replace(".md","")
#    print("Updating %s" % path)
    cm.write.create_output_file(page,path,name)
    return True

def update_hike_directory(hike):
  path = config['ExFilePath'] + "/" + get_target_directory(hike)
  updated = False
  for idx_file in glob.glob(path+"/*index*.md"):
    print("Processing %s" % idx_file)
    updated = updated or update_hike_links(idx_file,hike)

  return updated

args = parse_cli()
count = args.count
print("Fixing at most %d files" % count)

ExTarget = cm.msaccess.read(config['ExTargetPath'])
for hike in ExTarget:
  if update_hike_directory(hike):
    count = count - 1
  if count <= 0:
    print("Enough, exiting...")
    break
