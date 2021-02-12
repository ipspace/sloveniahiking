#
# Microsoft Access data handling library
#

import xml.etree.ElementTree as XMLTree

#
# Read exported Access table in XML format
#
def read(fname):
  table = XMLTree.parse(fname)
  data = []

  for in_row in table.getroot():
    row = {}
    for cell in in_row:
      row[cell.tag] = cell.text
    data.append(row)
  return data

def dictionary(list,key):
  dict = {}
  for row in list:
    if row.get(key):
      dict[row[key]] = row
  return dict