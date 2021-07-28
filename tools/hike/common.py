#
# Common hiking routines
#

difflevel_limits = {
  1 : { 'delta': 300, 'duration' : 2 },
  2 : { 'delta': 600, 'duration' : 4 },
  3 : { 'delta': 1000, 'duration' : 6 },
  4 : { 'delta': 8000, 'duration' : 24 }
}

def toNumber(s):
  try:
    return int(s)
  except:
    return float(s)

def set_hike_difflevel(hd):
  if 'difflevel' in hd:
    return

  for dl in sorted(difflevel_limits.keys()):
    found = True
    values = False
    for attr,maxv in difflevel_limits[dl].items():
      if attr in hd:
        values = True
        if isinstance(hd[attr],str):
          hd[attr] = toNumber(hd[attr])
        found = found and hd[attr] <= maxv
    if found and values:
      hd['difflevel'] = dl
      return

def cleanup(hd):
  for k in ('delta','duration','height'):
    if k in hd:
      if isinstance(hd[k],str):
        hd[k] = toNumber(hd[k])
