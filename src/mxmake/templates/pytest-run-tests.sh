{% extends "env.sh" %}

{% block env_content %}
pytest{% if testpaths %} \{% endif +%}
{% for path in testpaths %}
    {{ path }}{% if not loop.last %} \{% endif +%}
{% endfor %}

{% endblock %}
