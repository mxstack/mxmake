##############################################################################
# proxy targets
##############################################################################

{% for target in targets %}
.PHONY: {{ target["folder"] }}-{{ target["name"] }}
{{ target["folder"] }}-{{ target["name"] }}:
	$(MAKE) -C "./{{ target["folder"] }}/" {{ target["name"] }}

{% endfor %}