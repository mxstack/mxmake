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
#:[target.plone-site-recreate]
#:description = Removes the Plone instance from the database like in plone-site-purge,
#:              then creates a new one like in plone-site-create.
#:
#:[setting.PLONE_SITE_SCRIPT]
#:description = Path to the script to create or purge a Plone site
#:default = .mxmake/files/plone-site.py
#:#:
#:[setting.PLONE_SITE_CREATE_FAIL_IF_EXISTS]
#:description = Exit with an error if the Plone site already exists
#:default = True

#:[setting.PLONE_SITE_PURGE_FAIL_IF_NOT_EXISTS]
#:description = Exit with an error if the Plone site does not exists
#:default = True

##############################################################################
# plone
##############################################################################

.PHONY: plone-site-create
plone-site-create: $(ZOPE_RUN_TARGET)
	@echo "Creating Plone Site"
	@export PLONE_SITE_PURGE=False
	@export PLONE_SITE_CREATE=True
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)

.PHONY: plone-site-purge
plone-site-purge: $(ZOPE_RUN_TARGET)
	@echo "Purging Plone Site"
	@export PLONE_SITE_PURGE=True
	@export PLONE_SITE_CREATE=False
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)

.PHONY: plone-site-recreate
plone-site-recreate: $(ZOPE_RUN_TARGET)
	@echo "Purging Plone Site"
	@export PLONE_SITE_PURGE=True
	@export PLONE_SITE_CREATE=True
	@zconsole run $(ZOPE_INSTANCE_FOLDER)/etc/zope.conf $(PLONE_SITE_SCRIPT)
