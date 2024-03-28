#!/usr/bin/env python3
#
import cm.web
import cm.write

from wc.config import config
import os
import yaml
import cm.traverse
import cm.read
import cm.msaccess
import yaml

def sync_flower_data(path):
  si_page = cm.read.page(path)
  en_path = path.replace("index.md","index.en.md")
  if not os.path.exists(en_path):
    print(f"Cannot find {en_path}")
    return

  en_page = cm.read.page(en_path)
  en_yaml = yaml.dump(en_page)

  for k in si_page.keys():
    if k in ['title','layout','html','markdown','name']:
      continue

    if k not in en_page:
      print(f'{k} missing in {en_path}')
      en_page[k] = si_page[k]
      continue

    if en_page[k] != si_page[k]:
      print(f'{k} changed to {si_page[k]} in {en_path}')
      en_page[k] = si_page[k]

  if yaml.dump(en_page) != en_yaml:
    print(f"EN page {en_path} changed, updating...")
    cm.write.create_output_file(en_page,file_path=en_path)

cm.traverse.walk(config['FlowersContent'],r'index.md$',sync_flower_data)
