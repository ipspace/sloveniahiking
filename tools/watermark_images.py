#!/usr/local/lib/python3
import sys
from PIL import Image, ImageDraw, ImageFont

import cm.traverse

config = { \
  'ImagePath': '../static/images', \
  'Watermark_Font': 'Arial.ttf', \
  'Watermark_BG': '#908d8c', \
  'Watermark_FG': '#251f1e', \
  'Watermark_Text': '(C) Slovenia-Hiking.info' \
}

def watermark(p):
  img = Image.open(p)
  (w,h) = img.size
  draw = ImageDraw.Draw(img)
  draw.rectangle([0,int(h * 0.95),w,h],fill=config['Watermark_BG'])
  fnt = ImageFont.truetype(config['Watermark_Font'], int(h * 0.03))
  draw.text([int(w * 0.02),int(h * 0.956)],config['Watermark_Text'],font=fnt,fill=config['Watermark_FG'])
  img.save(p,'JPEG')
  print("Watermarked %s" % p)

cm.traverse.walk(config['ImagePath'],'(?i)M_.*\.JPG',watermark)
