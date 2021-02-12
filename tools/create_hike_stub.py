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

  print("Creating stub for %s from %s" % (target,path))
  page = cm.read.page(path)

  for k in ('markdown','draft','dirty','description'):
    page.pop(k,None)

  ExDirectory = page['name']
  data = ExData.get(ExDirectory,None)
  if not(data):
    print("... cannot find original data for %s" % ExDirectory)
    return

  page['title'] = data.get('ExEnglishName',page['title'])
  page['layout'] = 'stub'
  cm.write.create_output_file(page,os.path.dirname(target),name="index.en")

ExTarget = cm.msaccess.read(config['ExTargetPath'])
ExData = cm.msaccess.dictionary(ExTarget,'ExDirectory')

cm.traverse.walk(config['ExFilePath'],r'index\.md$',create_stub)
