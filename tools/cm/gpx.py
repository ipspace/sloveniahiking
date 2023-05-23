#
# GPX utilities
#

import os
import yaml
import gpxpy
import gpxpy.gpx

import cm.read
import cm.write

VERBOSE=False

def write_gpx_file(points,fname):
  # Create a GPX object, a track, and a track segment.
  # Bind them together
  #
  gpx = gpxpy.gpx.GPX()
  track = gpxpy.gpx.GPXTrack()
  gpx.tracks.append(track)
  segment = gpxpy.gpx.GPXTrackSegment()
  track.segments.append(segment)

  for p in points:
    gpoint = gpxpy.gpx.GPXTrackPoint(latitude=p['lat'], longitude=p['lon'],
                                      time=p['timestamp'], elevation=p['elevation'])
    segment.points.append(gpoint)

  print("Creating output file %s with %d points" % (fname,len(points)))
  with open(fname,"w") as out:
    out.write(gpx.to_xml())
    out.close()

def get_gpx_info(gpx_path):
  with open(gpx_path,'r') as gpxfile:
    gpx = gpxpy.parse(gpxfile)
    gpxfile.close()

  points = []
  for t in gpx.tracks:
    for s in t.segments:
      points.extend(list(s.points))

  lat_list = list(map(lambda x: x.latitude, points))
  lon_list = list(map(lambda x: x.longitude, points))

  info = {}
  info['min_lat'] = min(lat_list)
  info['min_lon'] = min(lon_list)
  info['max_lat'] = max(lat_list)
  info['max_lon'] = max(lon_list)
  info['center_lat'] = (info['min_lat']+info['max_lat'])/2
  info['center_lon'] = (info['min_lon']+info['max_lon'])/2
  info['delta_lat'] = (info['max_lat']-info['min_lat'])
  info['delta_lon'] = (info['max_lon']-info['min_lon'])
  return info

def sync_gpx_data(gpx_path):
  global VERBOSE

  if os.path.basename(gpx_path).find('_') == 0:
    print("Skipping %s" % gpx_path)
    return

  if VERBOSE:
    print("Found GPX file %s" % gpx_path)

  content_dir = os.path.dirname(gpx_path)
  index_name = None

  for idx_name in ('index.en.md','_index.en.md','index.md','_index.md'):
    if os.path.exists(content_dir+"/"+idx_name):
      index_name = content_dir+"/"+idx_name
      break

  if not index_name:
    print("Cannot find index file in %s" % content_dir)
    return

  page = cm.read.page(index_name)
  page_dump = yaml.dump(page)

  if not 'gpx' in page:
    page['gpx'] = {}
  else:
    if page['gpx'].get('modified',None) == os.path.getmtime(gpx_path):
      if VERBOSE:
        print("GPX timestamp match, exiting")
##      return

  page['gpx']['file'] = os.path.basename(gpx_path)
  page['gpx']['modified'] = int(os.path.getmtime(gpx_path))
  
  gpx_info = get_gpx_info(gpx_path)
  page['gpx']['center'] = { 'lat': gpx_info['center_lat'], 'lon': gpx_info['center_lon']}

##  print("%s: %s" % (gpx_path,gpx_info));
  old_zoom = page['gpx'].get('zoom',None)
  page['gpx']['zoom'] = 13

  if gpx_info['delta_lat'] < 0.023 and gpx_info['delta_lon'] < 0.055:
    page['gpx']['zoom'] = 14

  if gpx_info['delta_lat'] < 0.011 and gpx_info['delta_lon'] < 0.0260:
    page['gpx']['zoom'] = 15

  if gpx_info['delta_lat'] < 0.0065 and gpx_info['delta_lon'] < 0.0120:
    page['gpx']['zoom'] = 16

  if gpx_info['delta_lat'] > 0.049 or gpx_info['delta_lon'] > 0.12:
    page['gpx']['zoom'] = 12

  if yaml.dump(page) != page_dump:
    print("Page changed based on information in %s, updating..." % gpx_path)
    print(gpx_info)
    print(f"old zoom: {old_zoom}, new zoom: {page['gpx']['zoom']}")
    cm.write.create_output_file(page,file_path=index_name)
