# {{speaker_name}}

::::{grid} 2 2 2 2

:::{grid-item}
:columns: 4

```{image} ../images/speakers/{{renderyaml['picture']}}
:class: m-auto circular
:height: 300px
:width: 300px
```

:::

:::{grid-item}
:columns: 7
:child-align: center
{{renderyaml['bio']}}
:::

::::

## Talks (Eastern Timezone)

| Title | Abstract | Date | Time |
| ----- | -------- | ---- | ---- |
{% for talk in renderyaml['talks'] %}| {{ talk['title'] }} | {{ talk['abstract'] | replace("\n", " ") }} | {{ talk['date'] }} | {{ talk['time'] }} |
{% endfor %}