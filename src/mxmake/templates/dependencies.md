# Diagram

```{mermaid}

flowchart TD
{% for topic in topics %}
    subgraph {{ topic.title }}
{% for domain in topic.domains %}
        {{ domain.fqn }}[{{ domain.title }}]
{% endfor %}
    end
{% endfor %}
{% for topic in topics %}
{% for domain in topic.domains %}
    {{ domain.fqn }}[{{ domain.title }}]
{% for depends in domain.depends %}
    {{ domain.fqn }} --> {{ depends }}
{% endfor %}
{% for depends in domain.soft_depends %}
    {{ domain.fqn }} -.-> {{ depends }}
{% endfor %}
{% endfor %}
{% endfor %}

```