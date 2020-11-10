#
# Create output files
#
import yaml
import os

def create_output_file(data=None,target_path=None):
  text = data.get('markdown') or data.get('html')
  data.pop('markdown',None)
  data.pop('html',None)
  if not os.path.exists(target_path):
    os.makedirs(target_path)
  with open("%s/%s.md" % ( target_path,data['name'] ),"wt") as output:
    output.write('---\n')
    output.write(yaml.dump(data,allow_unicode=True))
    output.write('---\n')
    output.write(text)
    output.close()
