#
# Update page data from template
#

import cm.read
import os

def find_template(t,search_path):
  if os.path.exists(t):
    return t
  for d in search_path:
    if os.path.exists(d+"/"+t):
      return d+"/"+t
  raise("Cannot find template %s" % t)

def read_template(t,search_path=[]):
  return cm.read.data(find_template(t,search_path))

def update_items(page,parent_page=None,template={},lang=None):
  print("Use q to quit, - to erase\n")

  for (k,v) in template.items():
    page_v = page.get(k)

    if isinstance(v,dict):
      if lang in v:
        v = v.get(lang)

    if isinstance(v,list):
      print("Cannot handle list %s" % k)
      if not page_v:
        print("... setting parameter to default value")
        page[k] = v
        continue

    if not isinstance(v,dict):
      v = { 'default': v }

    if not page_v:
      page_v = v.get('default',None)
      if (not page_v) and v.get('inherit'):
        if isinstance(parent_page,dict):
          page_v = parent_page.get(k,None)
          print("Got value for %s from parent page: %s" % (k,page_v))

    if v.get('sample') and not page_v:
      prompt = "%s (sample: %s) ==> " % (k,v.get('sample'))
    else:
      prompt = "%s (now: %s) ==> " % (k,page_v)

    result = input(prompt)
    if result == "q":
      return
    elif result == "-":
      page_v = None
    elif result != "":
      if isinstance(v.get('default'),int):
        page_v = cm.read.number(result)
      else:
        page_v = result
    else:
      print("Kept %s at %s" % (k,page_v))      

    if v.get('despace') and isinstance(page_v,str):
      page_v = page_v.replace(" ","")
      page_v = page_v.replace("\n","")

    page[k] = page_v
    if page_v is None:
      page.pop(k,None)

  return page