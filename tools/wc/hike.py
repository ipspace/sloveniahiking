#
# Extract hike text from Zaplana.net web pages
#
import cm.cleanup
import cm.parse
import bs4
import yaml
import os
import re
import sys

def extract_element_text(td,figure):
  text = ""
  found_content = False
  for child in td.children:
    if isinstance(child,bs4.NavigableString):
      text = text + str(child)
    else:
      if child.name in ['span','div'] and "content" in child.get("id",""):
        text = text + extract_element_text(child,figure)
        found_content = True
      else:
        if (not found_content) or (not 'note' in child.get("class","")):
          text = text + cm.cleanup.html_element(child,do_figure=figure)
  return text
  
def extract_hike_text(html,figure=True):
  text = ""
  cm.cleanup.remove_style(html)
  cm.cleanup.remove_internal_links(html)
  cm.cleanup.img2figure(html)
  for td in html.find_all('td',id='content'):
    text = text + extract_element_text(td,figure)
  
  return cm.cleanup.whitespace(text)

def read_hike_page(url,subdir):
  html = bs4.BeautifulSoup(cm.web.fetch_html(url),"html.parser")

  page = {}
  cm.parse.extract_page_heading(page,html)
  lead = cm.parse.find_lead_image(html)
  if lead:
    page['lead'] = lead
  page['image'] = cm.parse.extract_images(html,remove_dir=subdir)
  page['text'] = extract_hike_text(html)
  return page

def get_target_directory(exrow):
  hike_dir = exrow.get('ExDirectory')
  subdir   = exrow.get('ExSubdirectory')
  target = hike_dir.split('/')[0]
  if subdir:
    target = target + "/" + subdir
  else:
    if '?' in hike_dir:
      target = hike_dir.split('/')[0]+"/"+hike_dir.split("=")[1]
  return target

def get_hike_prefix(exrow):
  hike_dir = exrow.get('ExDirectory')
  if "?" in hike_dir:
    if "/?pfx" in hike_dir:
      return hike_dir.split("/?pfx=")
    raise Exception("Don't know how to deal with hike directory %s" % hike_dir)
  else:
    return (hike_dir,"")

def read_hike(hike_data={},url_pattern=None):
  hike_dir = hike_data.get('ExDirectory')
  subdir = hike_data.get("ExSubdirectory")

  target = get_target_directory(hike_data)
  (hike_dir,hike_pfx) = get_hike_prefix(hike_data)

  if 'External' in hike_dir:
    print("Not handling external hikes at this time %s" % hike_dir)
    return
#  if '/' in hike_dir:
#    print("Have no idea how to handle subdirectory hikes %s" % hike_dir)
#    return
  print("Fetching %s target %s" % (hike_dir,target))

  text = ""
  first_page = ""
  section = 1

  hike = { 'image': [] }
  while True:
    page = read_hike_page(url_pattern % (hike_dir,section,"&pfx="+hike_pfx if hike_pfx else ""),subdir)
    if section == 1 and not page['text']:
      raise Exception('First page in a hike has no usable text')
    if not first_page:
      first_page = page['text']
    elif page['text'] == first_page:
      break

    h2 = page.get("h2","")
    if "Zemljevid" in h2 or "The map" in h2:
      hike['map'] = 1
    elif not "Rože ob poti" in h2 and not "Flora along" in h2:
      if page.get('h2') and section > 1:
        text = text + "<h2>%s</h2>\n" % page.get('h2')
      text = text + page['text']

    hike['image'] = hike['image'] + page['image']
    if page.get('lead') and not(hike.get('lead')):
      hike['lead'] = page['lead']
    section = section + 1

  hike['html'] = text
  hike['name'] = target
#  print(hike)
#  sys.exit(1)
  return hike

def augment_hike_data(hike,hike_data):
  hike['date'] = hike_data['ExChangeDate']
  hike['title'] = hike_data['ExName']
  hike['description'] = str(hike_data['ExDescription'])

  for k_from,k_to in {
        'ExAbsHeight':'height',
        'ExRelHeight':'delta',
        'ExTime':'duration',
        'ExLocX':'x',
        'ExLocY':'y',
        'ExTextAuthor':'author',
        'ExPhotoAuthor':'photo_author'}.items():
    v = hike_data.get(k_from)
    if v:
      hike[k_to] = v

  hike['dirty'] = True
  if '?' in hike_data['ExDirectory']:
    hike['multipath'] = True

  for k in ['height','delta','x','y','duration']:
    if hike.get(k):
      try:
        hike[k] = int(hike[k])
      except ValueError:
        hike[k] = float(hike[k])

  return

def fetch_hike_images(hike=None,url_pattern=None,target_pattern=None):
  hike_dir = hike['name']
  cm.web.fetch_images( \
    url_pattern=url_pattern % (hike_dir,'%s'), \
    target_dir=target_pattern % hike_dir , \
    image_list=hike.get('image',[]))

def fetch_hike(hike_row,config):
  if 'External' in hike_row['ExDirectory']:
    return

  target = get_target_directory(hike_row)
  for index_file in ['index.md','_index.md']:
    if os.path.exists('%s/%s/%s' % (config['ExFilePath'],target,index_file)):
      if not config.get('force'):
        print("%s has already been migrated, skipping" % hike_row['ExDirectory'])
        return
  
  hike = read_hike(hike_data=hike_row,url_pattern=config['HikeUrl'])
  if not hike:
    return

  hike['markdown'] = cm.cleanup.html_to_markdown(hike['html'])
  augment_hike_data(hike,hike_row)
  cm.write.create_output_file(data=hike,target_path=config['ExFilePath']+'/'+hike['name'],name='index')
  fetch_hike_images(hike=hike,url_pattern=config['HikeImageUrl'],target_pattern=config['ExFilePath']+'/%s')

  if '?' in hike_row['ExDirectory']:
    return
  if not cm.web.probe(config['HikeUrlEn'] % (hike_row['ExDirectory'],1,"")):
    return hike
  
  hike = read_hike(hike_data=hike_row,url_pattern=config['HikeUrlEn'],image_pattern=config['UrlImagePath'])
  if hike:
    hike['markdown'] = cm.cleanup.html_to_markdown(hike['html'])
    augment_hike_data(hike,hike_row)
    hike['title'] = hike_row.get('ExEnglishName',hike['title'])
    cm.write.create_output_file(data=hike,target_path=config['ExFilePathEn']+'/'+hike['name'],name='index.en')
    fetch_hike_images(hike=hike,url_pattern=config['HikeImageUrl'],target_pattern=config['ExFilePath']+'/%s')

  return hike
