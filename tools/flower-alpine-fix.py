#!/usr/bin/env python3
#
import cm.write

from wc.config import config
import argparse
from box import Box
import os

def parse_cli():
  parser = argparse.ArgumentParser(description='Fix alpine flower data')
  parser.add_argument('key', action='store',help='Lookup key')
  return parser.parse_args()

def find_subtaxa(f_data: Box, f_taxa: Box) -> None:
  for taxon in f_data:
    if taxon in f_taxa:
      continue
    t_comp = taxon.split(' ')
    t_nonvar = ' '.join(t_comp[:2])
    if t_nonvar in f_taxa:
      print(f"{taxon} --> {t_nonvar} {os.path.basename(os.path.dirname(f_taxa[t_nonvar]))}")

def build_genus(f_taxa: Box) -> Box:
  f_gen = Box(default_box=True,box_dots=True)
  for taxon in f_taxa.keys():
    t_comp = taxon.split(' ')
    t_gen  = t_comp[0]
    if t_gen not in f_gen:
      f_gen[t_gen] = []
    f_gen[t_gen].append(t_comp[1])

  return f_gen

args = parse_cli()
f_taxa = Box().from_yaml(filename=config['DataPath'] % 'flower_taxa.yml',default_box=True,box_dots=True)
f_gen  = build_genus(f_taxa)
f_alp  = Box().from_yaml(filename=config['DataPath'] % 'alps.yml',default_box=True,box_dots=True)
f_data = f_alp[args.key]

for taxon in f_data:
  if taxon in f_taxa:
    continue
  t_genus = taxon.split(' ')[0]
  if t_genus in f_gen:
    print(f'{taxon} {f_gen[t_genus]}')
