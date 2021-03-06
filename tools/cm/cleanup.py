#
# Common cleanup routines
#

import re
import subprocess
import bs4

def whitespace(text,cr=True,lf=False):
  if cr:
    text = text.replace('\r','')
  if lf:
    text = text.replace('\n',' ')
    text = text.replace('  ',' ')
    text = re.sub(r"\s\s+"," ",text)
    text = text.strip()
  return text

def figure_markup(element):
  src = ""
  for img in element.find_all('img'):
    src = img['src']
  if src:
    caption = whitespace(element.get_text(),cr=True,lf=True)
    return '{{--figure src="%s" caption="%s"--}}\n' % (src,caption)
  else:
    return str(element)

def nested_figure_table(element):
  text = ""
  for td in element.find_all('td',class_='image'):
    text = text + figure_markup(td)
  return text

#
# Called with a DIV element. It could be that the DIV element itself
# contains an image, or it could be that it contains a table with
# td.image
#
def figure(element):
  if element.find('td',class_='image'):
    return nested_figure_table(element)
  class_ = element.attrs.get('class','')
  if 'image' in class_.lower() or element.find('img'):
    return figure_markup(element)
  return str(element)

def get_cell_content(c):
  if c.find('p'):
    c = c.find('p')
  
  text = ""
  for t in c.contents:
    text = text + whitespace(str(t),cr=True,lf=True)
  return text

def table_to_dl(table):
  text = '<dl>\n'
  for row in table.find_all('tr'):
    cell_count = 0
    for cell in row.find_all(re.compile('^t[dh]')):
      cell_count = cell_count + 1
      tag = 'dt' if cell_count == 1 else 'dd'
      content = get_cell_content(cell)
      text = text + '<%s>%s</%s>\n' % (tag,content,tag)

  text = text + "</dl>\n"
  return text

def html_inner(e):
  text = ""
  for child in e.children:
    if isinstance(child,bs4.element.Tag):
      if child.find('td',class_='image') or ("{{--figure" in str(child)):
        text = text + html_inner(child)
        continue
    text = text + str(child)
  return text

def html_element(element,do_figure=True,do_table=True):
  text = str(element)
  if element.name == 'div':
    return html_inner(element)
  if element.name == 'table' and do_table:
    return table_to_dl(element)
  return text

def replace_shortcode(matchobject):
  sc = matchobject.group(0)
  sc = sc.replace('\\--','<',1)
  sc = sc.replace('\\--','>',1)
  sc = sc.replace('\\','')
  return sc

def insert_figure(matchobject):
  return '\n{{<figure src="%s">}}\n\n' % matchobject.group(1)

def cleanup_shortcode(md):
  md = re.sub('{{.*?}}',replace_shortcode,md)
  md = re.sub('!\\[\\]\\((.*?)\\)',insert_figure,md)
  return md

def html_to_markdown(html):
  result = subprocess.run( \
    "pandoc --from=html-native_divs-native_spans --to=markdown+definition_lists --column=9999 --wrap=none", \
    shell=True, check=True, \
    capture_output=True, \
    input=html,text=True)

  md = result.stdout
  return cleanup_shortcode(md)

def remove_style(html):
  for attr in ('lang','style','name'):
    for tag in html.findAll(lambda tag: tag.get(attr,None)):
      del(tag[attr])

  for tag in html.findAll(lambda tag: tag.get("class") and not "note" in tag.get("class","")):
    del(tag["class"])

def remove_internal_links(html):
  for a in html.find_all('a'):
    if a.get('href','').find('javascript') >= 0:
      del(a['href'])
    if a.get('href','').find('index.asp') >= 0:
      del(a['href'])

def figure_markup(src,caption):
  if not src:
    return
  if not caption:
    return '{{--figure src="%s"--}}\n' % (src)
  return '{{--figure src="%s" caption="%s"--}}\n' % (src,caption.strip())

def wrap2figure(wrap):
  text = ""
  src = ""
  caption = ""
  for element in wrap.children:
    if isinstance(element,bs4.element.NavigableString):
      caption = caption + str(element)
    elif element.name == "img":
      if src:
        text = text + figure_markup(src,caption)
      caption = ""
      src = element.get("src")
  
  if src:
    text = text + figure_markup(src,caption)
  wrap.string = text

def img2figure(html):
  while True:
    img = html.find(lambda tag: 
      tag.name == "img" and (tag.get("onclick",None) or not
        ("/" in tag.get("src","") or "map" in tag.get("src") or ".gif" in tag.get("src"))))
    if not img:
      break
    wrapper = img.parent
    if not wrapper \
       or not (wrapper.name in ['div','td','span']) \
       or (wrapper.name == 'span' and 'content' in wrapper.get('id')):
      markup = bs4.NavigableString(figure_markup(img.get("src"),None))
      img.replace_with(markup)
    else:
      wrap2figure(wrapper)
