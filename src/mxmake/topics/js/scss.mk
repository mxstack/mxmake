#:[scss]
#:title = SCSS Compiler
#:description = Compile Stylesheets using SCSS.
#:depends = js.npm
#:
#:[target.scss]
#:description = Run SCSS Stylesheet Compiler.
#:
#:[setting.SCSS_SOURCE]
#:description = The SCSS root source file.
#:default = scss/styles.scss
#:
#:[setting.SCSS_TARGET]
#:description = The target file for the compiles Stylesheet.
#:default = scss/styles.css
#:
#:[setting.SCSS_OPTIONS]
#:description = Additional options to be passed to SCSS compiler.
#:default = --no-source-map=none

##############################################################################
# scss
##############################################################################

# extend npm dev packages
NPM_DEV_PACKAGES+=sass

.PHONY: scss
scss: $(NPM_TARGET)
	@$(NPM_PREFIX)/node_modules/.bin/sass \
		$(SCSS_OPTIONS) $(SCSS_SOURCE) $(SCSS_TARGET)
