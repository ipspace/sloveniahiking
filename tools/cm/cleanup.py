#
# Common cleanup routines
#

import re
import subprocess

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
  if 'Image' in class_ or 'image' in class_:
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

def html_element(element,do_figure=True,do_table=True):
  text = str(element)
  if element.name == 'div' and do_figure:
    return figure(element)
  if element.name == 'table' and do_table:
    return table_to_dl(element)
  return text

def replace_shortcode(matchobject):
  sc = matchobject.group(0)
  sc = sc.replace('\\--','<',1)
  sc = sc.replace('\\--','>',1)
  sc = sc.replace('\\','')
  return sc

def cleanup_shortcode(md):
  md = re.sub('{{.*?}}',replace_shortcode,md)
  return md

def html_to_markdown(html):
  result = subprocess.run( \
    "pandoc --from=html --to=markdown+definition_lists --column=9999 --wrap=none", \
    shell=True, check=True, \
    capture_output=True, \
    input=html,text=True)

  md = result.stdout
  return cleanup_shortcode(md)
