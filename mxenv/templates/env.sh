{% extends "script.sh" %}

{% block script_content %}
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

{% block env_content %}{% endblock %}

unsetenv
{% endblock %}
