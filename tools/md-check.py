#!/usr/bin/env python3
#
# Scan the blog posts and create metadata and template files
#
# - blog archive data files
# - tag cloud (TBD)
#

import sys
import os
import argparse
import yaml
import json
import glob
from datetime import date, datetime, timezone
from termcolor import colored
import cm.read

LOGGING=False
VERBOSE=True
ERRORS=False

def parseCLI():
  parser = argparse.ArgumentParser(description='Check Markdown files (blog posts)')
  parser.add_argument('files', nargs='+',action='store',help='Files to check')
  parser.add_argument('--log', dest='logging', action='store_true',help='Enable basic logging')
  parser.add_argument('--verbose', dest='verbose', action='store_true',help='Enable more verbose logging')
  return parser.parse_args()

def reportError(err,path):
  global ERRORS
  print("%s in %s" % (err,path))
  ERRORS=True

def check_file(path):
  if VERBOSE:
    print("Reading file %s" % path)

  page = cm.read.page(path)
  text = page.get("markdown","")

  if not page:
    reportError("Cannot read markdown doc",path)
    return

  if "localhost:1313" in text.lower():
    reportError("Localhost link",path)

  if not page.get('title'):
    print("Title is missing",path)

args = parseCLI()
#LOGGING = args.logging or args.verbose
#VERBOSE = args.verbose

for entry in args.files:
  if "content" in entry:
    check_file(entry)

if ERRORS:
  sys.exit(1)
