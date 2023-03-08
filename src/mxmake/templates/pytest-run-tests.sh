{% extends "env.sh" %}

{% block env_content %}
{{ mxenv_path }}pytest \
{% for path in testpaths %}
    {{ path }}{% if not loop.last %} \{% endif %}

{% endfor %}
{% endblock %}
