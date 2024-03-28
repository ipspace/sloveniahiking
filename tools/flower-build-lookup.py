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
import hike.common
import yaml

f_lookup: dict = {}

def read_flower_page(path):
  global f_lookup

  page = cm.read.page(path)
  if 'latin' not in page:
    return
  
  l_name = page['latin']
  l_path = path.replace(config['FlowersContent'],'/flowers')
  f_lookup[l_name] = l_path

  l_comp = [ c for c in l_name.split(' ') if c not in ['subsp.','x','f.','var.' ] ]
  if len(l_comp) > 2:
    l_taxon = ' '.join(l_comp[:2])
    if not l_taxon in f_lookup:
      f_lookup[l_taxon] = l_path

cm.traverse.walk(config['FlowersContent'],r'index.md$',read_flower_page)
cm.write.create_output_file(f_lookup,file_path=(config['DataPath'] % 'flower_taxa.yml'))
