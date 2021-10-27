from jinja2 import Template
import copy
import yaml
import glob
from os import path
from datetime import date

# creating the date object of today's date
todays_date = date.today()
todays_year = str(todays_date.year)

# variables
talks_directory = path.join(path.dirname(__file__), '..', 'talks', todays_year)
templates_directory = path.join(path.dirname(__file__), 'templates')
agent_file = path.join(path.dirname(__file__), '..', 'docs', todays_year, 'agenda.md')

print(f'[+] Processing files inside {talks_directory} directory')

# ******** Open every forge yaml file available ****************
print("  [>] Opening forge yaml files..")
yaml_files = glob.glob(path.join(talks_directory, "*.yaml"))
yaml_loaded = [yaml.safe_load(open(yf).read()) for yf in yaml_files]

# ******** Open forge template ****************
print("  [>] Reading template..")
yaml_template = Template(open(path.join(templates_directory, "table_template.md")).read())

# Create Markdown file
print("  [>] Writing docs to markdown ..")
yaml_for_render = copy.deepcopy(yaml_loaded)

# Generate the markdown
markdown = yaml_template.render(renderyaml=yaml_for_render)
open(agent_file, 'w').write(markdown)