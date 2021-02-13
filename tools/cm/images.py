#
# Image handling routines
#

import os
import shutil
from PIL import Image, ImageDraw, ImageFont

config = {
  'ImagePath': '../static/images',
  'Watermark_Font': 'Arial.ttf',
  'Watermark_BG': '#908d8c',
  'Watermark_FG': '#251f1e',
  'Watermark_Text': '(C) sloveniahiking.rocks',
  'Thumb_Size': ( 1024,1024 )
}

def get_default_author(p):
  return config['Watermark_Text']

def watermark(p,author=get_default_author):
  img = Image.open(p)
  if config.get('Thumb_Size'):
    img.thumbnail(config['Thumb_Size'])
  (w,h) = img.size
  draw = ImageDraw.Draw(img)
  draw.rectangle([0,int(h * 0.95),w,h],fill=config['Watermark_BG'])
  fnt = ImageFont.truetype(config['Watermark_Font'], int(h * 0.03))
  draw.text([int(w * 0.02),int(h * 0.956)],author(p),font=fnt,fill=config['Watermark_FG'])
  img.save(p,'JPEG')
  print("Watermarked %s" % p)

def replace_image(p,lookup={},do_watermark=True):
  original = lookup.get(os.path.basename(p),None)
  if original:
    if len(original) > 1:
      print("Original for %s has multiple options, replace manually\n%s" % (p,original))
    else:
      print("Replacing %s with %s" % (p,original[0]))
      shutil.copyfile(original[0],p)
      if do_watermark:
        watermark(p)
  else:
    print("Original not found: %s" % p)

