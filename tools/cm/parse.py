#
# Common HTML parsing routines
#

def recover_image_name(src):
  return src.replace('L_','M_').replace('T_','M_')

def extract_images(html,dir):
  imglist = []
  for image in html.find_all('img'):
    src = image['src']
    image.attrs.pop('width',None)
    image.attrs.pop('height',None)
    if not '..' in src and src.find('/') != 0 and src.find('://') < 0:
      src = recover_image_name(src)
      imglist.append(src)
      image['src'] = dir+"/"+src
  return imglist

def find_lead_image(html):
  for image in html.find_all('img'):
    src = image['src']
    if not '..' in src and 'L_' in src:
      return recover_image_name(src)

def extract_page_heading(page,html):
  for banner in html.find_all('div',class_='nBanner'):
    if banner.h1:
      page['h1'] = banner.h1.text
    if banner.h2:
      page['h2'] = banner.h2.text

  if page.get('h1') or page.get('h2'):
    return

  h1 = html.find('p',class_='BannerFirstRow')
  if h1:
    page['h1'] = h1.text

  h2 = html.find('p',class_='BannerSecondRow')
  if h2:
    page['h2'] = h2.text
