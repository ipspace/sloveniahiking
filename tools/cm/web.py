#
# Common web fetching routines
#
import urllib.request
import os
import subprocess

#
# Fetch HTML from a URL
def fetch_html(url):
  print("Fetching %s" % url)
  try:
    with urllib.request.urlopen(url) as response:
      return response.read()
  except urllib.error.HTTPError as e:
    print("Request to %s failed with %d, trying to recover" % (url,e.code))
    return e.read()

#
# Probe a URL
def probe(url):
  print("Probing %s" % url)
  try:
    urllib.request.urlopen(url)
    return True
  except urllib.error.URLError:
    return False

#
# Fetch images
def fetch_images(url_pattern=None,target_dir=None,image_list=[]):
  for src in image_list:
    dst = target_dir + "/" + src
    if os.path.exists(dst):
      print("%s already exists, skipping" % dst)
    else:
      dst_dir = os.path.dirname(dst)
      if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

      url = url_pattern % src
      print("Fetching %s into %s" % (url,dst))
      subprocess.run( \
        "curl -s '%s' --output %s" % (url,dst), \
      shell=True, check=True)
