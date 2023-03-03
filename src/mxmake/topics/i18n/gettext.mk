#:[gettext]
#:title = Gettext
#:description = Provide targets for working with gettext
#:
#:[target.gettext-create]
#:description = Create message catalogs for all defined languages if not exists.
#:
#:[target.gettext-update]
#:description = Update translations.
#:
#:[target.gettext-compile]
#:description = Compile message catalogs.
#:
#:[setting.GETTEXT_LOCALES_PATH]
#:description = Path of directory containing the message catalogs.
#:default = locale
#:
#:[setting.GETTEXT_DOMAIN]
#:description = Translation domain to use.
#:default =
#:
#:[setting.GETTEXT_LANGUAGES]
#:description = List of language identifiers.
#:default =

##############################################################################
# gettext
##############################################################################

# case `system.dependencies` domain is included
SYSTEM_DEPENDENCIES+=gettext

.PHONY: gettext-create
gettext-create:
	@if [ ! -e "$(GETTEXT_LOCALES_PATH)/$(GETTEXT_DOMAIN).pot" ]; then \
		echo "Create pot file"; \
		mkdir -p $(GETTEXT_LOCALES_PATH); \
		touch $(GETTEXT_LOCALES_PATH)/$(GETTEXT_DOMAIN).pot; \
	fi
	@for lang in $(GETTEXT_LANGUAGES); do \
		if [ ! -e "$(GETTEXT_LOCALES_PATH)/$$lang/LC_MESSAGES/$(GETTEXT_DOMAIN).po" ]; then \
			mkdir -p $(GETTEXT_LOCALES_PATH)/$$lang/LC_MESSAGES; \
			msginit \
				-i $(GETTEXT_LOCALES_PATH)/$(GETTEXT_DOMAIN).pot \
				-o $(GETTEXT_LOCALES_PATH)/$$lang/LC_MESSAGES/$(GETTEXT_DOMAIN).po \
				-l $$lang; \
		fi \
	done

#.PHONY: gettext-update
#gettext-update:
#	@echo "Update translations"

#echo "Update translations"
#for po in "$GETTEXT_LOCALES_PATH"/*/LC_MESSAGES/$GETTEXT_DOMAIN.po; do
#    msgmerge -o "$po" "$po" "$GETTEXT_LOCALES_PATH"/$GETTEXT_DOMAIN.pot
#done

#.PHONY: gettext-compile
#gettext-compile:
#	@echo "Compile message catalogs"

#echo "Compile message catalogs"
#for po in "$GETTEXT_LOCALES_PATH"/*/LC_MESSAGES/*.po; do
#	lg=${po##$GETTEXT_LOCALES_PATH/}
#	lg=${lg%%/LC_MESSAGES/*}
#	echo -n "$lg: "
#	msgfmt --statistics -o "${po%.*}.mo" "$po"
#done

