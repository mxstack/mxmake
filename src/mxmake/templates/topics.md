{% for topic in topics %}

---

# {{ topic.title }}

{{ topic.description }}

{% for domain in topic.domains %}

---
## {{ domain.title }}

{{ domain.description }}

| Property | Value |
|----------|-------|
| **FQN** | `{{ domain.fqn }}` |
{% if domain.depends or domain.soft_depends %}
| **Dependencies** | {% if domain.depends %}**Hard:** {% for depend in domain.depends %}`{{ depend }}`{% if not loop.last %}, {% endif %}{% endfor %}{% if domain.soft_depends %}<br>{% endif %}{% endif %}{% if domain.soft_depends %}**Soft:** {% for soft_depend in domain.soft_depends %}`{{ soft_depend }}`{% if not loop.last %}, {% endif %}{% endfor %}{% endif %} |
{% endif %}

{% if domain.targets %}

**Targets:**

| Target | Description |
|--------|-------------|
{% for target in domain.targets %}
| `{{ target.name }}` | {{ target.description | replace('\n', '<br>') }} |
{% endfor %}
{% endif %}

{% if domain.settings %}

**Settings:**

| Setting | Description | Default |
|---------|-------------|---------|
{% for setting in domain.settings %}
| `{{ setting.name }}` | {{ setting.description | replace('\n', '<br>') }} | `{{ setting.default }}` |
{% endfor %}
{% endif %}

{% endfor %}
{% endfor %}
