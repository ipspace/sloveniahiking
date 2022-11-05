#!/usr/local/lib/python3
import sys
from PIL import Image, ImageDraw, ImageFont

import cm.traverse
import cm.images

cm.traverse.walk(config['ImagePath'],'(?i)M_.*\.JPG',cm.images.watermark)
