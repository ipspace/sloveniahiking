#
# Read various thingies like Hugo documents
#

import sys
import re
import yaml
from datetime import date, datetime, timezone
import dateutil.parser
import dateutil.tz

YAML_DELIMITER="---\n"

def page(path):
  with open(path, 'r') as stream:
    content = re.split(YAML_DELIMITER,stream.read())
    if len(content) < 2:
      return (None,None)
    frontmatter = content[1]
    text = YAML_DELIMITER.join(content[2:])
    stream.close()

  try:
    doc = yaml.safe_load(frontmatter)
  except yaml.YAMLError as exc:
    raise Exception("Error parsing YAML header in %s: %s" % (path,exc))

  # Parsing the publication date is weird
  #
  # * YAML might already have generated the datetime timestamp, so we have to go to string first
  # * We have to use dateutil.parser so we can parse 'meaningful' and ISO timestamps
  # * The result might or might not have a timezone, so we have to adjust that as well
  #
  date = doc.get('date')
  if date:
    try:
      pubdate = dateutil.parser.parse(str(date))
    except:
      raise Exception("Date %s parsing error %s in %s" % (date,sys.exc_info()[0],path))

    if pubdate.tzinfo is None:
      pubdate = pubdate.replace(tzinfo=timezone.utc)
    doc['date'] = pubdate

  doc['markdown'] = text
  return doc