#:[python-ldap]
#:title = Python LDAP
#:description = Builds and installs python-ldap against local OpenLDAP
#:depends =
#:  core.mxenv
#:  ldap.openldap
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

# case `system.dependencies` domain is included
SYSTEM_DEPENDENCIES+=python3-dev libldap2-dev libssl-dev libsasl2-dev

PYTHON_LDAP_TARGET:=$(SENTINEL_FOLDER)/python-ldap.sentinel
$(PYTHON_LDAP_TARGET): $(MXENV_TARGET) $(OPENLDAP_TARGET)
	@$(PYTHON_PACKAGE_COMMAND) install \
		--force-reinstall \
		python-ldap
	@touch $(PYTHON_LDAP_TARGET)

.PHONY: python-ldap
python-ldap: $(PYTHON_LDAP_TARGET)

.PHONY: python-ldap-dirty
python-ldap-dirty:
	@rm -f $(PYTHON_LDAP_TARGET)

.PHONY: python-ldap-clean
python-ldap-clean: python-ldap-dirty
	@test -e $(MXENV_PYTHON) && $(MXENV_PYTHON) -m pip uninstall -y python-ldap || :

INSTALL_TARGETS+=python-ldap
DIRTY_TARGETS+=python-ldap-dirty
CLEAN_TARGETS+=python-ldap-clean
