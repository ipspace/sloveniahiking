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

def extract_hike_text(html,figure=True):
  text = ""
  cm.cleanup.remove_style(html)
  cm.cleanup.remove_internal_links(html)
  cm.cleanup.img2figure(html)
  for td in html.find_all('td',id='content'):
    for span in td.find_all(re.compile('^(span|div)'),id='content'):
      for element in span.contents:
        text = text + cm.cleanup.html_element(element,do_figure=figure)
  return cm.cleanup.whitespace(text)

def read_hike_page(url,hike_dir,image_dir):
  html = bs4.BeautifulSoup(cm.web.fetch_html(url),"html.parser")

  page = {}
  cm.parse.extract_page_heading(page,html)
  lead = cm.parse.find_lead_image(html)
  if lead:
    page['lead'] = lead
  page['image'] = cm.parse.extract_images(html,None)
  page['text'] = extract_hike_text(html)
  return page

def read_hike(hike_data={},url_pattern=None,image_pattern=None):
  if hike_data.get('ExTextAuthor'):
    return

  hike_dir = hike_data.get('ExDirectory')
  image_dir = image_pattern % hike_dir

  if 'External' in hike_dir:
    print("Not handling external hikes at this time %s" % hike_dir)
    return
  if 'pfx=' in hike_dir:
    print("Have no idea how to handle multi-path hikes %s" % hike_dir)
    return
  if '/' in hike_dir:
    print("Have no idea how to handle subdirectory hikes %s" % hike_dir)
    return
  print("Fetching %s" % hike_dir)

  text = ""
  first_page = ""
  section = 1

  hike = { 'image': [] }
  while True:
    page = read_hike_page(url_pattern % (hike_dir,section),hike_dir,image_dir)
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
  return hike

def augment_hike_data(hike,hike_data):
  hike['date'] = hike_data['ExChangeDate']
  hike['name'] = hike_data['ExDirectory']
  hike['title'] = hike_data['ExName']
  hike['description'] = str(hike_data['ExDescription'])
  hike['height'] = hike_data['ExAbsHeight']

  if 'ExRelHeight' in hike_data:
    hike['delta'] = hike_data['ExRelHeight']

  if 'ExTime' in hike_data:
    hike['duration'] = hike_data['ExTime']

  hike['x'] = hike_data.get('ExLocX')
  hike['y'] = hike_data.get('ExLocY')
  hike['draft'] = True

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
  if os.path.exists('%s/%s/index.md' % (config['ExFilePath'],hike_row['ExDirectory'])):
    if not config.get('force'):
      print("%s has already been migrated, skipping" % hike_row['ExDirectory'])
      return

  hike = read_hike(hike_data=hike_row,url_pattern=config['HikeUrl'],image_pattern=config['UrlImagePath'])
  if not hike:
    return

  hike['markdown'] = cm.cleanup.html_to_markdown(hike['html'])
  augment_hike_data(hike,hike_row)
  cm.write.create_output_file(data=hike,target_path=config['ExFilePath']+'/'+hike['name'],name='index')
  fetch_hike_images(hike=hike,url_pattern=config['HikeImageUrl'],target_pattern=config['ExFilePath']+'/%s')

  if not cm.web.probe(config['HikeUrlEn'] % (hike_row['ExDirectory'],1)):
    return hike
  
  hike = read_hike(hike_data=hike_row,url_pattern=config['HikeUrlEn'],image_pattern=config['UrlImagePath'])
  if hike:
    hike['markdown'] = cm.cleanup.html_to_markdown(hike['html'])
    augment_hike_data(hike,hike_row)
    hike['title'] = hike_row.get('ExEnglishName',hike['title'])
    cm.write.create_output_file(data=hike,target_path=config['ExFilePathEn']+'/'+hike['name'],name='index.en')
    fetch_hike_images(hike=hike,url_pattern=config['HikeImageUrl'],target_pattern=config['ExFilePath']+'/%s')

  return hike
