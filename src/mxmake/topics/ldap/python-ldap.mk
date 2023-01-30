#:[python-ldap]
#:title = Python LDAP
#:description = Builds and installs python-ldap against local OpenLDAP
#:depends = ldap.openldap
#:
#:[target.python-ldap]
#:descriptions = Build and install python-ldap
#:
#:[target.python-ldap-dirty]
#:descriptions = Rebuild python-ldap on next make run.
#:
#:[target.python-ldap-clean]
#:descriptions = Uninstall python-ldap

##############################################################################
# python-ldap
##############################################################################

PYTHON_LDAP_TARGET:=$(SENTINEL_FOLDER)/python-ldap.sentinel
$(PYTHON_LDAP_TARGET): $(MXENV_TARGET) $(OPENLDAP_TARGET)
	@$(MXENV_PATH)pip install \
		--force-reinstall \
		--no-use-pep517 \
		--global-option=build_ext \
		--global-option="-I$(OPENLDAP_DIR)/include" \
		--global-option="-L$(OPENLDAP_DIR)/lib" \
		--global-option="-R$(OPENLDAP_DIR)/lib" \
		python-ldap
	@touch $(PYTHON_LDAP_TARGET)

.PHONY: python-ldap
python-ldap: $(PYTHON_LDAP_TARGET)

.PHONY: python-ldap-dirty
python-ldap-dirty:
	@rm -f $(PYTHON_LDAP_TARGET)

.PHONY: python-ldap-clean
python-ldap-clean: python-ldap-dirty
	@test -e $(MXENV_PATH)pip && $(MXENV_PATH)pip uninstall -y python-ldap

INSTALL_TARGETS+=python-ldap
DIRTY_TARGETS+=python-ldap-dirty
CLEAN_TARGETS+=python-ldap-clean
