#
# Create output files
#
import yaml
import os

def create_output_file(data=None,target_path=None,name=None,file_path=None):
  text = data.get('markdown') or data.get('html')
  data.pop('markdown',None)
  data.pop('html',None)
  if file_path:
    target_path = os.path.dirname(file_path)
  if not os.path.exists(target_path):
    os.makedirs(target_path)
  if not file_path:
    fname = name or data.get('name','index')
    file_path = "%s/%s.md" % ( target_path,fname )
  with open(file_path,"wt") as output:
    print(".. Creating output file %s" % file_path)
    output.write('---\n')
    output.write(yaml.dump(data,allow_unicode=True))
    output.write('---\n')
    if text:
      output.write(text)
    output.close()
