#
# Image handling routines
#

import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ExifTags

config = {
  'ImagePath': '../static/images',
  'Watermark_Font': 'Arial.ttf',
  'Watermark_BG': '#908d8c',
  'Watermark_FG': '#251f1e',
  'Watermark_Text': '© sloveniahiking.rocks',
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
  draw.text( \
    [int(w * 0.02),int(h * 0.956)], \
    author(p) or config['Watermark_Text'], \
    font=fnt, \
    fill=config['Watermark_FG'])
  img.save(p,'JPEG')
  print("Watermarked %s" % p)

def replace_image(p,lookup={},do_watermark=True,author=get_default_author):
  try:
    img = Image.open(p)
    (w,h) = img.size
    if (w >= 1024) or (h >= 1024):
      print("Image %s already updated, skipping..." % p)
      return
  except:
    pass
  original = lookup.get(os.path.basename(p),None)
  if original:
    if len(original) > 1:
      print("Original for %s has multiple options, replace manually\n%s" % (p,original))
    else:
      print("Replacing %s with %s" % (p,original[0]))
      shutil.copyfile(original[0],p)
      if do_watermark:
        watermark(p,author)
  else:
    print("Original not found: %s" % p)

def get_exif(img):
  exif_raw = Image.open(img).getexif()
  if exif_raw is None:
    return None

  exif = {}
  for k,v in exif_raw.items():
    if k in ExifTags.TAGS:
      exif[ExifTags.TAGS[k]] = v

  if 'GPSInfo' in exif:
    try:
      gpsinfo = {}
      for key in exif['GPSInfo'].keys():
        decode = ExifTags.GPSTAGS.get(key,key)
        gpsinfo[decode] = exif['GPSInfo'][key]
      exif['GPSInfo'] = gpsinfo
    except:
      pass

  return exif
