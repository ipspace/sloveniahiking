#
#
import cm.msaccess

from wc.config import config
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

def updateFile(hike_file):
  page = cm.read.page(hike_file)
  md = page.get('markdown',None)

  if not md:
    return False

  imgpath = "/images/hikes/"+page["name"]+"/"
  md = md.replace(imgpath,"")
  if md.find("/images/") > 0:
    print("Cannot replace an image reference in %s" % page["name"])
  if md != page.get('markdown'):
    page['markdown'] = md
    print("Updating: "+hike_file)
    cm.write.create_output_file(page,os.path.dirname(hike_file),os.path.basename(hike_file).replace(".md",""))
    return True

  return False

args = parse_cli()
count = args.count
print("Fixing at most %d files" % count)
path = config['ExFilePath']

for hike_file in glob.glob(path+'/*/index*.md'):
  if hike_file.find("/_") >= 0:
    print("Index file"+hike_file)
    continue

  if updateFile(hike_file):
    count = count - 1
  if count <= 0:
    break
