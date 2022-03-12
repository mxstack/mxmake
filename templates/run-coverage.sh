{% extends "env.sh" %}

{% block env_content %}
sources=(
{% for path in sourcepaths %}
    {{ path }}
{% endfor %}
)

sources=$(printf ",%s" "${sources[@]}")
sources=${sources:1}

{{ venv }}/bin/coverage run \
    --source=$sources \
    -m zope.testrunner --auto-color --auto-progress \
{% for path in testpaths %}
    --test-path={{ path }}{% if not loop.last %} \{% endif %}

{% endfor %}

{{ venv }}/bin/coverage report
{{ venv }}/bin/coverage html
{% endblock %}
