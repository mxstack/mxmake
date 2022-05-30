{% extends "script.sh" %}

{% block script_content %}
{% if env -%}
function setenv() {
{% for name, value in env.items() %}
    export {{ name }}="{{ value }}"
{% endfor %}
}

function unsetenv() {
{% for name in env %}
    unset {{ name }}
{% endfor %}
}

trap unsetenv ERR INT

setenv
{% endif %}
{% block env_content %}{% endblock %}
{% if env -%}
unsetenv
{%- endif %}
{% endblock %}
