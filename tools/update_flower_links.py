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

def createFlowerLookup(data):
  lookup = { 'fname' : {}}
  for row in data:
    fname = os.path.basename(row['RelativeURL'])
    lookup['fname'][fname] = row
  return lookup

def addFamilyLookup(data,lookup = { 'fname' : {} }):
  for row in data:
    lookup['fname']['l_'+row['LatinFamily'].lower()+'.htm'] = row
    lookup['fname']['druzina_list_si.asp?family='+row['LatinFamily']] = row
    lookup['fname']['druzina_list_si.asp?name=latin&family='+row['LatinFamily']] = row

def addGenusLookup(data,lookup = { 'fname' : {} }):
  for row in data:
    lookup['fname']['l_'+row['BotanyGenus'].lower()+'.htm'] = row
    lookup['fname']['si_'+row['BotanyGenus']+'.asp'] = row

    if row['BotanyGenus'] == 'Lilium':
      lookup['fname']['SI_lilije.asp'] = row
    if row['BotanyGenus'] == 'Polygonatum':
      lookup['fname']['Salomonov_pecat.asp'] = row

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

def createRelativeFlowerLink(flower):
  if flower.get('LatinName'):
    return "../../"+flower['LatinName'].lower().replace(' ','')+'/'+flower['SlovenianName'].lower().replace(' ','-')+'/'

  if flower.get('LatinFamily'):
    print("WARNING: Need family l_"+flower['LatinFamily'].lower()+".htm")
    return '../../family/'+flower['LatinFamily'].lower()+'/'

  if flower.get('BotanyGenus'):
    print("WARNING: Need genus l_"+flower['BotanyGenus'].lower()+".htm")
    return '../../genus/'+flower['BotanyGenus'].lower()+'/'

  raise Exception("Don't know how to deal with link data %s" % flower)

def lookupLink(link):
  global flower_lookup
  global family_lookup

  if link.find('http') == 0:
    if link.find('zaplana') > 0:
      raise Exception("External link to zaplana.net: %s" % link)
    return link

  if link[len(link) - 1] == '/':
    return link

  if link.find('/images/') > 0:
    if link.find('/flowers') > 0:
      return link
    return link.replace('/images/','/../images/flowers/')

  fname = os.path.basename(link)
  flower = flower_lookup['fname'].get(fname,None)
  if flower:
    return createRelativeFlowerLink(flower)

  raise Exception("Cannot figure out link %s" % link)

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
flower_lookup = createFlowerLookup(flower_data)
addFamilyLookup(cm.msaccess.read(config['ExFlowersFamilyPath']),flower_lookup)
addGenusLookup(cm.msaccess.read(config['ExFlowersGenusPath']),flower_lookup)

for flower in flower_data:
  if updateLinks(flower):
    count = count - 1
  if count <= 0:
    break
