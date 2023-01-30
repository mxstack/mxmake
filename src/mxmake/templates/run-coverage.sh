{% extends "env.sh" %}

{% block env_content %}
sources=(
{% for path in sourcepaths %}
    {{ path }}
{% endfor %}
)

sources=$(printf ",%s" "${sources[@]}")
sources=${sources:1}

{% if omitpaths -%}
omits=(
{% for path in omitpaths %}
    {{ path }}
{% endfor %}
)

omits=$(printf ",%s" "${omits[@]}")
omits=${omits:1}
{%- endif %}

{{ mxenv_path }}coverage run \
    --source=$sources \
{% if omitpaths %}
    --omit=$omits \
{% endif %}
    -m zope.testrunner --auto-color --auto-progress \
{% for path in testpaths %}
    --test-path={{ path }}{% if not loop.last %} \{% endif %}

{% endfor %}

{{ mxenv_path }}coverage report
{{ mxenv_path }}coverage html
{% endblock %}
