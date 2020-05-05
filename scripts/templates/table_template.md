# Agenda (Eastern Time)

|Time|topic|
| :---| :---|
|10:00am-10:15am|Welcome<br>Roberto Rodriguez [@Cyb3rWard0g](http://twitter.com/@Cyb3rWard0g), Microsoft MSTIC|
{% for talk in renderyaml|sort(attribute='time') %}|{{talk['time']}}|<b>{{talk['title']}}</b><br>{{talk['speaker']}}{% if talk['twitter'] %}{% set handle = talk['twitter'].split('@') %} [{{talk['twitter']}}](http://twitter.com/{{handle[1]}}){% endif %}, {{talk['company']}}<br><br><b>Description</b><br>{{talk['abstract']}}|
{% endfor %}