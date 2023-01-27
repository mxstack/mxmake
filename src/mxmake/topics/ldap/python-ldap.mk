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
$(PYTHON_LDAP_TARGET): $(VENV_TARGET) $(OPENLDAP_TARGET)
	@$(VENV_SCRIPTS)pip install \
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
	@test -e $(VENV_SCRIPTS)pip && $(VENV_SCRIPTS)pip uninstall -y python-ldap

DEV_INSTALL_TARGETS+=python-ldap
DEV_DIRTY_TARGETS+=python-ldap-dirty
DEV_CLEAN_TARGETS+=python-ldap-clean
