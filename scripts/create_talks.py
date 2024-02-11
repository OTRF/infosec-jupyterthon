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
# Assuming yaml_loaded is a list of dictionaries loaded from your YAML files
speakers_dict = {}

for yaml_doc in yaml_loaded:
    if yaml_doc.get('speaker'):
        for speaker in yaml_doc['speaker']:
            speaker_name = speaker.get('name')
            if speaker_name:
                # Prepare the talk details
                talk_details = {
                    'title': yaml_doc.get('title'),
                    'abstract': yaml_doc.get('abstract'),
                    'date': yaml_doc.get('date'),
                    'time': yaml_doc.get('time')
                }
                # Check if the speaker already exists in the dictionary
                if speaker_name not in speakers_dict:
                    speakers_dict[speaker_name] = {
                        'job_title': speaker.get('job_title'),
                        'company': speaker.get('company'),
                        'twitter': speaker.get('twitter'),
                        'github': speaker.get('github'),
                        'picture': speaker.get('picture'),
                        'bio': speaker.get('bio'),
                        'talks': [talk_details]
                    }
                else:
                    # Append the talk details to the existing speaker's list of talks
                    speakers_dict[speaker_name]['talks'].append(talk_details)

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
for speaker_name, speaker_details in speakers_dict.items():
    print(f'[+] Creating {speaker_name} markdown ...')
    yaml_template = Template(open(path.join(templates_directory, "speaker_template.md")).read())

    # Prepare data for rendering by making a deep copy of the speaker's details
    yaml_for_render = copy.deepcopy(speaker_details)

    # Generate the markdown
    file_name = (speaker_name.lower()).replace(' ','_') + '.md'
    markdown = yaml_template.render(renderyaml=yaml_for_render, speaker_name=speaker_name)
    open(f'{docs_directory}/{todays_year}/speakers/{file_name}', 'w').write(markdown)

    # Update toc file
    for caption in toc_yaml['parts']:
        if f'{todays_year} Edition' in caption['caption']:
            for chapter in caption['chapters']:
                if 'speakers' in chapter['file']:
                    if 'sections' not in chapter.keys():
                        chapter['sections'] = list()
                    speaker_dict = dict()
                    speaker_dict['file'] = todays_year + '/speakers/' + str(file_name.split('.md')[0])
                    if speaker_dict not in chapter['sections']:
                        chapter['sections'].append(speaker_dict)

print("[+] Writing final TOC file for Jupyter book..")
with open(toc_file, 'w') as file:
    yaml.dump(toc_yaml, file, sort_keys=False)