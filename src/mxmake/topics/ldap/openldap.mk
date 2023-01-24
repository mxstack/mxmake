#:[openldap]
#:title = OpenLDAP
#:description = Builds OpenLDAP from source
#:depends = core.base
#:
#:[target.openldap]
#:description = Download and build OpenLDAP from source.
#:
#:[target.openldap-dirty]
#:description = Rebuild OpenLDAP on next make run.
#:
#:[target.openldap-clean]
#:description = Remove local OpenLDAP build.
#:
#:[setting.OPENLDAP_VERSION]
#:description = OpenLDAP version to download
#:default = 2.4.59
#:
#:[setting.OPENLDAP_URL]
#:description = OpenLDAP base download URL
#:default = https://www.openldap.org/software/download/OpenLDAP/openldap-release/
#:
#:[setting.OPENLDAP_DIR]
#:description = Build directory for OpenLDAP
#:default = $(shell echo $(realpath .))/openldap
#:
#:[setting.OPENLDAP_ENV]
#:description = Build environment for OpenLDAP
#:default = PATH=/usr/local/bin:/usr/bin:/bin

##############################################################################
# openldap
##############################################################################

OPENLDAP_SENTINEL:=$(SENTINEL_FOLDER)/openldap.sentinel
$(OPENLDAP_SENTINEL): $(SENTINEL)
	@echo "Building openldap server in '$(OPENLDAP_DIR)'"
	@test -d $(OPENLDAP_DIR) || curl -o openldap-$(OPENLDAP_VERSION).tgz \
		$(OPENLDAP_URL)/openldap-$(OPENLDAP_VERSION).tgz
	@test -d $(OPENLDAP_DIR) || tar xf openldap-$(OPENLDAP_VERSION).tgz
	@test -d $(OPENLDAP_DIR) || rm openldap-$(OPENLDAP_VERSION).tgz
	@test -d $(OPENLDAP_DIR) || mv openldap-$(OPENLDAP_VERSION) $(OPENLDAP_DIR)
	@env -i -C $(OPENLDAP_DIR) $(OPENLDAP_ENV) bash -c \
		'./configure \
			--with-tls \
			--enable-slapd=yes \
			--enable-overlays \
			--prefix=$(OPENLDAP_DIR) \
		&& make depend \
		&& make -j4 \
		&& make install'
	@touch $(OPENLDAP_SENTINEL)

.PHONY: openldap
openldap: $(OPENLDAP_SENTINEL)

.PHONY: openldap-dirty
openldap-dirty:
	@test -d $(OPENLDAP_DIR) \
		&& env -i -C $(OPENLDAP_DIR) $(OPENLDAP_ENV) bash -c 'make clean'
	@rm -f $(OPENLDAP_SENTINEL)

.PHONY: openldap-clean
openldap-clean:
	@rm -f $(OPENLDAP_SENTINEL)
	@rm -rf $(OPENLDAP_DIR)
