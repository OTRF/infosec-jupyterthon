from jinja2 import Template
import copy
import yaml
import glob
from os import path

print("[+] Processing files inside {} directory".format('../talks'))
# ******** Open every forge yaml file available ****************
print("  [>] Opening forge yaml files..")
yaml_files = glob.glob(path.join(path.dirname(__file__), '../talks', "*.yaml"))
yaml_loaded = [yaml.safe_load(open(yf).read()) for yf in yaml_files]

# ******** Open forge template ****************
print("  [>] Reading template..")
yaml_template = Template(open("templates/table_template.md").read())

# Create Markdown file
print("  [>] Writing docs to markdown ..")
yaml_for_render = copy.deepcopy(yaml_loaded)

# Generate the markdown
markdown = yaml_template.render(renderyaml=yaml_for_render)
open('../docs/2020/agenda.md', 'w').write(markdown)