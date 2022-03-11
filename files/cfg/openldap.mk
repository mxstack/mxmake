###############################################################################
# openldap
###############################################################################

OPENLDAP_VERSION:="2.4.59"
OPENLDAP_URL:="https://www.openldap.org/software/download/OpenLDAP/openldap-release/"
OPENLDAP_DIR:=$(shell echo $(realpath .))/openldap
OPENLDAP_ENV:="PATH=/usr/local/bin:/usr/bin:/bin"
OPENLDAP_SENTINEL:=$(SENTINEL_FOLDER)/openldap.sentinel

.PHONY: openldap
openldap: $(OPENLDAP_SENTINEL)

$(OPENLDAP_SENTINEL): $(SENTINEL)
	@echo "$(OK_COLOR)Building openldap server in $(OPENLDAP_DIR) $(NO_COLOR)"
	@rm -rf openldap
	@curl -o openldap-$(OPENLDAP_VERSION).tgz $(OPENLDAP_URL)/openldap-$(OPENLDAP_VERSION).tgz
	@tar xf openldap-$(OPENLDAP_VERSION).tgz
	@rm openldap-$(OPENLDAP_VERSION).tgz
	@mv openldap-$(OPENLDAP_VERSION) openldap
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
