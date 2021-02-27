#
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

#args = parse_cli()
#config['force'] = args.force

def is_a_page(target):
  if not os.path.isfile(target):
    return False
  page = cm.read.page(target)
  return page.get('layout','') != 'stub'

def create_stub(path):
  target = path.replace("index.md","index.en.md")
  if is_a_page(target):
#    print("%s is a full-blown page, skipping" % target)
    return

  if is_a_page(target.replace("_","")):
    print("%s has an alternate full-blown page, skipping" % target)
    return

#  print("Creating stub for %s from %s" % (target,path))
  page = cm.read.page(path)

  for k in ('markdown','draft','dirty','description'):
    page.pop(k,None)

  ExDirectory = page.get('name')
  if not ExDirectory:
    print("Cannot figure out the hike name in %s" % path)
    return
  
  data = ExData.get(ExDirectory,None)
  if not(data) and '/' in ExDirectory:
    subdir = ExDirectory.split('/')[1]
    data = ExSubDir.get(subdir,None)

  if not(data):
    lookup = ExDirectory.split('/')[0]+"/?pfx="+subdir
    print("... trying alternate lookup key %s" % lookup)
    data = ExData.get(lookup)

  if not(data):
    print("... cannot find original data for %s" % ExDirectory)
    return

  page['title'] = data.get('ExEnglishName',page['title'])
  page['layout'] = 'stub'
  fname = os.path.basename(target).replace('.md','')
  cm.write.create_output_file(page,os.path.dirname(target),name=fname)

ExTarget = cm.msaccess.read(config['ExTargetPath'])
ExData = cm.msaccess.dictionary(ExTarget,'ExDirectory')
ExSubDir = cm.msaccess.dictionary(ExTarget,'ExSubdirectory')

cm.traverse.walk(config['ExFilePath'],r'index\.md$',create_stub)
