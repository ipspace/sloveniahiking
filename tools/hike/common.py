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

def set_hike_difflevel(hd,levels = difflevel_limits):
  if 'difflevel' in hd:
    return

  for dl in sorted(levels.keys()):
    found = True
    values = False
    for attr,maxv in levels[dl].items():
      if attr in hd:
        values = True
        if isinstance(hd[attr],str):
          hd[attr] = toNumber(hd[attr])
        found = found and hd[attr] <= maxv
    if found and values:
      hd['difflevel'] = dl
      return

def cleanup(hd):
  for k in ('delta','duration','height','length'):
    if k in hd:
      if isinstance(hd[k],str):
        hd[k] = toNumber(hd[k])
