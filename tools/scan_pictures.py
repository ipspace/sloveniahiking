#
#
import cm.msaccess

from wc.config import config
import sys
import yaml
import argparse
import os
import glob
import re

def parse_cli():
  parser = argparse.ArgumentParser(description='Update flower links')
  parser.add_argument('--src',dest='source',default='/Volumes/Pictures/Roze', \
    action='store',help='Input directory tree',required=True)
  parser.add_argument('--dest',dest='dest', \
    action='store',help='Destination YAML file',required=True)
  parser.add_argument('-v',dest='verbose',action='store_true',help='Verbose printout')
  parser.add_argument('-q',dest='quiet',action='store_true',help='Be as quiet as possible')
  parser.add_argument('--count',dest='count',default=9999,type=int,action='store',help='Maximum number of hikes to import')

#  parser.add_argument('--force',dest='force',action='store_true',help='Reread the hike')
  return parser.parse_args()

def add_photo_data(data,dest,fpath):
  global args
  if args.verbose:
    print("%s --> %s" % (fpath,dest))
  list = data.get(dest,[])

  if len(list) > 0:
    fsize = os.stat(fpath).st_size
    for pfile in list:
      if fsize == os.stat(pfile).st_size:
        if not args.quiet:
          print("Duplicate picture:\n  %s\n  %s" % (fpath,pfile))
        return

    if "Originals" in fpath:
      if not args.quiet:
        print("Ignoring non-edited file: %s" % fpath)
      return

    print("Potential collision:\n  %s\n  %s" % (list,fpath))

  list.append(fpath)
  data[dest] = list

def add_photo(data,fpath):
  global args

  # Old-style syntax ddd-dddd_IMG.JPG
  fname = os.path.basename(fpath)
  m = re.fullmatch('\\d{2}(\\d-\\d{4}_IMG.JPG)',fname,re.IGNORECASE)
  if m:
    add_photo_data(data,"M_"+m.group(1),fpath)
    return

  m = re.fullmatch('\\d{2}(\\d_\\d{4,5}.JPG)',fname,re.IGNORECASE)
  if m:
    add_photo_data(data,"M_"+m.group(1),fpath)
    return

  m = re.fullmatch('P\\d(\\d+.JPG)',fname,re.IGNORECASE)
  if m:
    add_photo_data(data,"M_"+m.group(1),fpath)
    return

  m = re.fullmatch('IM(G_\\d{4,5}.JPG)',fname,re.IGNORECASE)
  if m:
#    print("Figure out this name format %s" % fpath)
    add_photo_data(data,"M_"+m.group(1),fpath)
    return

  m = re.fullmatch('\\d{2}(\\d+.JPG)',fname,re.IGNORECASE)
  if m:
    add_photo_data(data,"M_"+m.group(1),fpath)
    return

  m = re.fullmatch('[MT]_.*',fname,re.IGNORECASE)
  if m:
    if not args.quiet:
      print("Skipping %s" % fpath)
    return

  if not args.quiet:
    print("Cannot figure out photo name %s" % fpath)

def scan_directory(src,data):
  global count
  global args
  if args.verbose:
    print("Scanning directory %s" % src)
  for fname in glob.glob(src+'/*'):
    if 'jpg' in fname.lower() or 'jpeg' in fname.lower():
      add_photo(data,fname)
      count = count + 1
      if count > args.count:
        print("Count exceeded")
        sys.exit(1)
    if os.path.isdir(fname):
      if "Neznano" in fname:
        continue
      scan_directory(fname,data)

args = parse_cli()
data = {}
count = 0
scan_directory(args.source,data)
with open(args.dest,"w") as output:
  output.write(yaml.dump(data))
  output.close
