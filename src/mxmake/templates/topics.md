{% for topic in topics %}

---

# {{ topic.name }}

{% for domain in topic.domains %}

---
## {{ domain.title }}

{{ domain.description }}

FQN
: `{{ domain.fqn }}`

{% if domain.depends %}
Depends on
{% for depend in domain.depends %}
: `{{ depend }}`
{% endfor %}
{% endif %}

{% if domain.targets %}
Targets
{% for target in domain.targets %}
: `{{ target.name }}`

  : {{ target.description | indent(4) }}

{% endfor %}
{% endif %}

{% if domain.settings %}
Settings
{% for setting in domain.settings %}
: `{{ setting.name }}`

  : {{ setting.description | indent(4) }}

  : Default: `{{ setting.default | indent(4) }}`

{% endfor %}
{% endif %}

{% endfor %}
{% endfor %}
