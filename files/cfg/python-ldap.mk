###############################################################################
# python-ldap
###############################################################################

.PHONY: python-ldap
python-ldap: openldap venv
	@$(PIP_BIN) install \
		--no-use-pep517 \
		--global-option=build_ext \
		--global-option="-I$(OPENLDAP_DIR)/include" \
		--global-option="-L$(OPENLDAP_DIR)/lib" \
		--global-option="-R$(OPENLDAP_DIR)/lib" \
		python-ldap
