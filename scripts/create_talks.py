from jinja2 import Template
import copy
import yaml
import glob
from os import path
from datetime import date, datetime
import calendar

# creating the date object of today's date
todays_date = date.today()
todays_year = str(todays_date.year)

# variables
talks_directory = path.join(path.dirname(__file__), '..', 'talks', todays_year)
docs_directory = path.join(path.dirname(__file__), '..', 'docs')
templates_directory = path.join(path.dirname(__file__), 'templates')
agenda_file = path.join(docs_directory, todays_year, 'agenda.md')
toc_file = path.join(docs_directory, "_toc.yml")

print(f'[+] Processing files inside {talks_directory} directory')

# ******** Open every talk yaml file available ****************
print("  [>] Opening talk yaml files..")
yaml_files = glob.glob(path.join(talks_directory, "*.yaml"))
yaml_loaded = [yaml.safe_load(open(yf).read()) for yf in yaml_files]

# ******* Create Agenda List **********
agenda_files = dict()
format = "%Y-%m-%d"
for yaml_doc in yaml_loaded:
    dt_object = datetime.strptime(yaml_doc['date'], format)
    day = "_".join((str(dt_object.weekday()), calendar.day_name[dt_object.weekday()],  calendar.month_name[dt_object.month], str(dt_object.day)))
    if day not in agenda_files.keys():
        agenda_files[day] = list()
    agenda_files[day].append(yaml_doc)

# ******* Create Speakers List **********
speakers_list = list()
for yaml_doc in yaml_loaded:
    if yaml_doc['speaker']:
        for speaker in yaml_doc['speaker']:
            if speaker not in speakers_list:
                speakers_list.append(speaker)

# ******** Open Agenda template ****************
print("  [>] Reading template..")
yaml_template = Template(open(path.join(templates_directory, "agenda_template.md")).read())

# Create Markdown file
print("  [>] Writing docs to markdown ..")
yaml_for_render = copy.deepcopy(agenda_files)

# Generate the markdown
markdown = yaml_template.render(renderyaml=yaml_for_render, todaysYear=todays_year)
open(agenda_file, 'w').write(markdown)

# ******** Read Jupyter Book TOC File ******
toc_yaml = yaml.safe_load(open(toc_file).read())

# ******** Process Speakers *********
for speaker in speakers_list:
    speaker_name = speaker['name']
    print(f'[+] Creating {speaker_name} markdown ..')
    yaml_template = Template(open(path.join(templates_directory, "speaker_template.md")).read())

    # Create Markdown file
    yaml_for_render = copy.deepcopy(speaker)

    # Generate the markdown
    file_name = (speaker_name.lower()).replace(' ','_') + '.md'
    markdown = yaml_template.render(renderyaml=yaml_for_render, speaker_name=speaker_name)
    open(f'{docs_directory}/{todays_year}/speakers/{file_name}', 'w').write(markdown)

    # Update toc file
    for caption in toc_yaml['parts']:
        if caption['caption'] == 'Editions':
            for chapter in caption['chapters']:
                if todays_year in chapter['file']:
                    for section in chapter['sections']:
                        if 'speakers' in section['file']:
                            if 'sections' not in section.keys():
                                section['sections'] = list()
                            speaker_dict = dict()
                            speaker_dict['file'] = todays_year + '/speakers/' + str(file_name.split('.md')[0])
                            if speaker_dict not in section['sections']:
                                section['sections'].append(speaker_dict)

print("[+] Writing final TOC file for Jupyter book..")
with open(toc_file, 'w') as file:
    yaml.dump(toc_yaml, file, sort_keys=False)