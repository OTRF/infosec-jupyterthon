# Agenda (Eastern Timezone)
{% for key, value in renderyaml| dictsort(by='key') %}
{% set list = key.split('_') %}
{% raw %}````{tab}{% endraw %} {{ list[1] }} {% raw %}({% endraw %}{{ list[2] }} {{ list[3] }}{% raw %}){% endraw %}
|Time|Session|
| :---| :---|
{% for talk in value |sort(attribute='time') %}|{{talk['time']}}|<b>{{talk['title']}}{% if talk['binder'] %} [![Binder](https://mybinder.org/badge_logo.svg)]({{talk['binder']}}){% endif %}</b><br><br>{% if talk['abstract'] %}{{talk['abstract']}}<br><br>{% endif %}{% if talk['speaker'] %}{% for speaker in talk['speaker'] %}[{{speaker['name']}}](https://infosecjupyterthon.com/{{todaysYear}}/speakers/{{speaker['name'].lower() | replace(" ","_") }}.html){% if speaker['twitter'] %}{% set handle = speaker['twitter'].split('@') %} [{{speaker['twitter']}}](http://twitter.com/{{handle[1]}}){% endif %}, {{speaker['job_title']}}, {{speaker['company']}}<br>{% endfor %}{% endif %}|
{% endfor %}{% raw %}````{% endraw %}
{% endfor %}