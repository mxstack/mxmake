{% for topic in topics %}

---

# {{ topic.title }}

{{ topic.description }}

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

{% if domain.soft_depends %}
Soft depends on
{% for soft_depends in domain.soft_depends %}
: `{{ soft_depends }}`
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
