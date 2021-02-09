#
# Extract flower text from Zaplana.net web pages
#
import cm.cleanup
import cm.parse
import bs4
import yaml
import os
import re
import string
import html

def capitalizeURL(t):
  return string.capwords(t).replace(' ','')

def flowerFilePath(flower_row,config):
  return config['FlowersPath'] % (flower_row['BotanyFamily'],capitalizeURL(flower_row['LatinName']))

def extract_text(html,figure=True):
  text = ""
  for d in html.find_all('div',id='content'):
    # Remove HREF from all Javascript links
    for a in d.find_all('a'):
      if a.get('href','').find('javascript') >= 0:
        del(a['href'])

    # Remove LANG, STYLE and CLASS attribute

    for attr in ('lang','style','class'):
      for tag in d.findAll(lambda tag: tag.get(attr,None)):
        del(tag[attr])

    # Regular cleanup - skip images, tables, image DIV, and "more info" footer
    for element in d.contents:
      if isinstance(element,bs4.element.Tag):
        if element.name == 'img':
          continue
        if element.name == 'table':
          print("WARNING... TABLE")
          continue
        if element.get('id') == 'InsertPictures':
          continue
        if str(element).find('Več informacij') >= 0:
          break
      text = text + str(element)
  return cm.cleanup.whitespace(text)

def read_flower(fdata={},topURL=None,imageURL=None):
  url = topURL+fdata['RelativeURL']
  html = bs4.BeautifulSoup(cm.web.fetch_html(url),"html.parser")

  result = {}
  cm.parse.extract_page_heading(result,html)

  lead = cm.parse.find_lead_image(html)
  if lead:
    result['lead'] = lead
  else:
    result['lead'] = cm.parse.recover_image_name(os.path.basename(fdata['LeadImage']))

  result['image'] = cm.parse.extract_images(html,imageURL)
  if not result['image']:
    result['image'] = [result['lead']]
  result['html'] = extract_text(html)
  return result

data_map = {
  'LatinName': 'latin',
  'BotanyOrder': 'order',
  'BotanyFamily': 'family',
  'FlowerColor': 'color',
  'FlowerType': 'flower_type',
  'Petals': 'petals',
  'PhotoAuthor': 'author',
  'FlowerStart': 'f_start',
  'FlowerEnd': 'f_end',
  'AddDate': 'date'
}

data_bool_map = {
  'StarFlower': 'star_shape',
  'PetalsJoined': 'petals_joined',
  'Parallel': 'parallel',
  'GoodSample': 'lead_sample'
}
def augment_flower_data(f,fd,topURL):
  f['title'] = html.unescape(fd['SlovenianName'])
#  f['url'] = topURL + fd['RelativeURL']
  for (fn,tn) in data_map.items():
    if fd.get(fn):
      f[tn] = fd.get(fn)

  for (fn,tn) in data_bool_map.items():
    v = fd.get(tn)
    f[tn] = True if v and v != '0' else False

  return

def fetch_flower(flower_row,config):
  path = flowerFilePath(flower_row,config)
  topURL = config['FlowersTopURL']
  imagePath = topURL+os.path.dirname(flower_row['LeadImage'])+'/%s'

  if os.path.exists(path + '/index.md'):
    if not config.get('force'):
      print("%s has already been migrated, skipping" % flower_row['LatinName'])
      return

  flower = read_flower(fdata=flower_row,topURL=topURL,imageURL=imagePath)
  if not flower:
    return

  flower['markdown'] = cm.cleanup.html_to_markdown(flower['html'])
  augment_flower_data(flower,flower_row,config['FlowersTargetURL'])

  flower['name'] = 'index'
  cm.web.fetch_images( \
    url_pattern=imagePath, \
    target_dir=path, \
    image_list=flower.get('image',[]))
  cm.write.create_output_file(data=flower,target_path=path)

  flower['path'] = path
  return flower

def write_en_stub(frow,fdata,cfg):
  fdata['name'] = 'index.en'
  fdata.pop('html',None)
  fdata.pop('markdown',None)
  fdata.pop('url',None)
  fdata['title'] = frow.get('EnglishName') or frow.get('LatinName')
  cm.write.create_output_file(data=fdata,target_path=fdata.pop('path'))
