#:[plone]
#:title = plone
#:description = Plone application related
#:depends = applications.zope
#:
#:[target.plone-site-create]
#:description = Creates a Plone site using the script provided in `PLONE_SITE_SCRIPT` configuration.
#:
#:[target.plone-site-purge]
#:description = Removes the Plone instance from the database, but the database itself is kept.
#:
#:[setting.PLONE_SITE_SCRIPT]
#:description = Path to the script to create or purge a Plone site
#:default = .mxmake/files/plone-site.py

##############################################################################
# plone
##############################################################################

.PHONY: plone-site-create
plone-site-create: $(ZOPE_RUN_TARGET)
	@echo "Creating Plone Site"
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)

.PHONY: plone-site-purge
plone-site-purge: $(ZOPE_RUN_TARGET)
	@echo "Purging Plone Site"
	@export PLONE_SITE_PURGE=True
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)
