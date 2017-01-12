# This is a generic Makefile. It will only work on systems with GNU make.

# This is written to 'prefix' in 'build' rule, then read in 'install'
prefix=/usr/local
TARGET = $(DESTDIR)$(prefix)

PACKAGE = debreate
VERSION = 0.7.13
BINDIR = bin
DATAROOT = share
DATADIR = $(DATAROOT)/$(PACKAGE)
APPSDIR = $(DATAROOT)/applications
PIXDIR = $(DATAROOT)/pixmaps
ICONTHEME = $(DATAROOT)/icons/gnome
MIMEDIR = $(DATAROOT)/mime/packages
MIMEICONSDIR = $(ICONTHEME)/scalable/mimetypes

PERM_DATA = 0644
PERM_EXEC = 0755

INSTALL_DATA = install -vm ${PERM_DATA}
INSTALL_EXEC = install -vm ${PERM_EXEC}
INSTALL_FOLDER = cp -vR
MKDIR = mkdir -vp
UNINSTALL = rm -vf

define MOVE =
	target_dir=$2; \
	source_file=$1; \
	if [ ! -d "$${target_dir}" ]; then \
		$(MKDIR) "$${target_dir}"; \
	fi; \
	mv -vf "$${source_file}" "$${target_dir}"; \
	target_file="$${target_dir}/$$(basename $${source_file})"; \
	chmod -c $(PERM_DATA) "$${target_file}"
endef

UNINSTALL_FOLDER = find "$1" -type f -print -delete; find "$1" -type d -empty -print -delete


FILES_executable = \
	init.py

FILES_root = \
	command_line.py \
	main.py

PKG_wiz_bin = wiz_bin/*.py

PKG_dbr = dbr/*.py
PKG_globals = globals/*.py

FILES_extra = \
	README.md \
	INFO

FILES_doc = \
	docs/changelog \
	docs/LICENSE.txt \
	docs/usage.pdf

FILES_man = \
	man/man1/$(PACKAGE).1

FILES_dist = \
	$(FILES_executable) \
	$(FILES_root) \
	$(FILES_extra) \
	Makefile

DIR_bitmaps = bitmaps
DIR_locale = locale
DIR_templates = templates

FILES_BUILD = \
	$(FILES_root) \
	$(PKG_dbr) \
	$(FILES_doc) \
	$(FILES_executable) \
	$(PKG_globals) \
	$(PKG_wiz_bin)

DIRS_dist = \
	$(DIR_bitmaps) \
	$(DIR_locale) \
	$(DIR_templates) \
	data \
	dbr \
	debian \
	docs \
	globals \
	man \
	scripts \
	wiz_bin

PACKAGE_dist = $(PACKAGE)_$(VERSION).tar.xz

FILE_launcher = debreate.desktop
FILE_mime = data/mime/$(PACKAGE).xml
INSTALLED = INSTALLED

MIME_icons = data/svg/application-x-dbp.svg

all:
	@echo "\n\tNothing to be done"; \
	echo "\trun one of the following:"; \
	echo "\n\t\t`tput bold`make install`tput sgr0` to install Debreate"; \
	echo "\t\t`tput bold`make help`tput sgr0`    to show a list of options\n"; \

$(INSTALLED)_file:
	@echo "Creating \"$(INSTALLED)\" file ..."; \
	echo "prefix=$(prefix)\n" > "$(INSTALLED)"; \

install: $(FILES_BUILD) $(DIR_locale) $(INSTALLED)_file install-bitmaps install-launcher install-man install-mime install-templates
	@target=$(DESTDIR)$(prefix); \
	bindir=$${target}/$(BINDIR); \
	datadir=$${target}/$(DATADIR); \
	pixdir=$${target}/$(PIXDIR); \
	\
	echo "\nprefix set to $(prefix)"; \
	echo "Install target set to $${target}\n"; \
	\
	mkdir -vp "$${target}/$(DATADIR)"; \
	for py in $(FILES_executable); do \
		$(INSTALL_EXEC) "$${py}" "$${datadir}"; \
	done; \
	for py in $(FILES_root) $(EXTRA_FILES); do \
		$(INSTALL_DATA) "$${py}" "$${datadir}"; \
	done; \
	\
	mkdir -vp "$${datadir}/dbr"; \
	for py in $(PKG_dbr); do \
		$(INSTALL_DATA) "$${py}" "$${datadir}/dbr"; \
	done; \
	\
	mkdir -vp "$${datadir}/wiz_bin"; \
	for py in $(PKG_wiz_bin); do \
		$(INSTALL_DATA) "$${py}" "$${datadir}/wiz_bin"; \
	done; \
	\
	mkdir -vp "$${datadir}/globals"; \
	for py in $(PKG_globals); do \
		$(INSTALL_DATA) "$${py}" "$${datadir}/globals"; \
	done; \
	\
	$(MKDIR) "$${datadir}/docs"; \
	for doc in $(FILES_doc); do \
		$(INSTALL_DATA) "$${doc}" "$${datadir}/docs"; \
	done; \
	\
	$(INSTALL_FOLDER) $(DIR_locale) "$${datadir}"; \
	\
	$(MKDIR) "$${bindir}"; \
	ln -vfs "$(prefix)/$(DATADIR)/init.py" "$${bindir}/$(PACKAGE)"; \
	\
	$(MKDIR) "$${pixdir}"; \
	$(INSTALL_DATA) "bitmaps/debreate64.png" "$${pixdir}/debreate.png"; \
	\
	$(call MOVE,$(INSTALLED),$${datadir}); \

uninstall: uninstall-bitmaps uninstall-launcher uninstall-man uninstall-mime uninstall-templates
	@target=$(DESTDIR)$(prefix); \
	bindir=$${target}/$(BINDIR); \
	datadir=$${target}/$(DATADIR); \
	appsdir=$${target}/$(APPSDIR); \
	pixdir=$${target}/$(PIXDIR); \
	\
	echo "\nprefix set to $(prefix)"; \
	echo "Uninstall target set to $${target}\n"; \
	\
	$(UNINSTALL) "$${pixdir}/debreate.png"; \
	$(UNINSTALL) "$${bindir}/$(PACKAGE)"; \
	\
	if [ -d "$${datadir}" ]; then \
		for f in `find "$${datadir}" -type f`; do \
			$(UNINSTALL) "$${f}"; \
		done; \
		find "$${datadir}" -type d -empty -delete; \
	fi; \

install-bitmaps: $(DIR_bitmaps)
	@target="$(DESTDIR)$(prefix)"; \
	data_dir="$${target}/$(DATADIR)"; \
	if [ ! -d "$${data_dir}" ]; then \
		$(MKDIR) "$${data_dir}"; \
	fi; \
	$(INSTALL_FOLDER) "$(DIR_bitmaps)" "$${data_dir}"; \

uninstall-bitmaps:
	@target="$(DESTDIR)$(prefix)"; \
	bitmaps_dir="$${target}/$(DATADIR)/bitmaps"; \
	if [ -d "$${bitmaps_dir}" ]; then \
		$(call UNINSTALL_FOLDER,$${bitmaps_dir}); \
	fi; \

install-icons: $(MIME_icons)
	@target="$(DESTDIR)$(prefix)"; \
	icons_dir="$${target}/$(MIMEICONSDIR)"; \
	$(MKDIR) "$${icons_dir}"; \
	for i in $(MIME_icons); do \
		$(INSTALL_DATA) "$${i}" "$${icons_dir}"; \
	done; \

uninstall-icons:
	@target="$(DESTDIR)$(prefix)"; \
	icons_dir="$${target}/$(ICONTHEME)"; \
	if [ -d "$${icons_dir}" ]; then \
		find "$${icons_dir}" -type f -name "application-x-dbp*" -print -delete; \
		find "$${icons_dir}" -type d -empty -print -delete; \
	fi; \

install-launcher: data/$(FILE_launcher)
	@apps_dir=$(TARGET)/$(APPSDIR); \
	$(MKDIR) "$${apps_dir}"; \
	$(INSTALL_DATA) "data/$(FILE_launcher)" "$${apps_dir}"; \

uninstall-launcher:
	@apps_dir=$(TARGET)/$(APPSDIR); \
	$(UNINSTALL) "$${apps_dir}/$(FILE_launcher)"; \

install-man: $(FILES_man)
	@target="$(DESTDIR)$(prefix)"; \
	data_root="$${target}/$(DATAROOT)"; \
	for f in $(FILES_man); do \
		filename=$$(basename "$${f}") && mandir="$${data_root}/$$(dirname $${f})"; \
		if [ ! -d "$${mandir}" ]; then \
			$(MKDIR) "$${mandir}"; \
		fi; \
		$(INSTALL_DATA) "$${f}" "$${mandir}"; \
		gzip -vf9 "$${mandir}/$${filename}"; \
	done; \

uninstall-man:
	@target="$(DESTDIR)$(prefix)"; \
	man_dir="$${target}/$(DATAROOT)/man"; \
	echo "Manual dir: $${man_dir}"; \
	find "$${man_dir}/man1" -type f -name "$(PACKAGE)\.1\.gz" -delete; \

install-mime: $(FILE_mime) install-icons
	@target="$(DESTDIR)$(prefix)"; \
	mime_dir="$${target}/$(MIMEDIR)"; \
	if [ ! -d "$${mime_dir}" ]; then \
		$(MKDIR) "$${mime_dir}"; \
	fi; \
	$(INSTALL_DATA) "$(FILE_mime)" "$${mime_dir}"; \

uninstall-mime: uninstall-icons
	@target="$(DESTDIR)$(prefix)"; \
	mime_dir="$${target}/$(MIMEDIR)"; \
	$(UNINSTALL) "$${mime_dir}/$(PACKAGE).xml"; \

install-templates: $(DIR_templates)
	@target="$(DESTDIR)$(prefix)"; \
	data_dir="$${target}/$(DATADIR)"; \
	if [ ! -d "$${data_dir}" ]; then \
		$(MKDIR) "$${data_dir}"; \
	fi; \
	$(INSTALL_FOLDER) "$(DIR_templates)" "$${data_dir}"; \

uninstall-templates:
	@target="$(DESTDIR)$(prefix)"; \
	templates_dir="$${target}/$(DATADIR)/templates"; \
	if [ -d "$${templates_dir}" ]; then \
		$(call UNINSTALL_FOLDER,$${templates_dir}); \
	fi; \

dist: deb-clean
	@echo "Creating distribution package ..."
	@if [ -f "$(PACKAGE_dist)" ]; then \
		rm -v "$(PACKAGE_dist)"; \
	fi
	@tar -cJf "$(PACKAGE_dist)" $(FILES_dist) $(DIRS_dist)
	@file "$(PACKAGE_dist)"

clean:
	@find ./ -type f -name "*.pyc" -print -delete; \
	rm -vf "./bin/$(PACKAGE)"; \
	if [ -d "./bin" ]; then \
		$(call UNINSTALL_FOLDER,./bin); \
	fi; \
	rm -vf "./prefix"; \
	rm -vf "$(INSTALLED)"; \

distclean: clean deb-clean
	@rm -vf "$(PACKAGE_dist)"

debianize: dist
	@dh_make -y -n -c mit -e antumdeluge@gmail.com -f "$(PACKAGE_dist)" -p "$(PACKAGE)_$(VERSION)" -i

deb-bin: deb-clean
	@debuild -b -uc -us

deb-bin-signed: deb-clean
	@debuild -b -sa

deb-src: deb-clean
	@debuild -S -uc -us

deb-src-signed: deb-clean
	@debuild -S -sa

deb-clean:
	@rm -vrf "debian/$(PACKAGE)"
	@DEBUILD_FILES="\
	debian/debhelper-build-stamp debian/$(PACKAGE).debhelper.log \
	debian/$(PACKAGE).substvars debian/files"; \
	rm -vf $${DEBUILD_FILES}; \

help:
	@echo "Usage:"; \
	\
	echo "\tmake [command]\n"; \
	\
	echo "Commands:"; \
	\
	echo "\thelp"; \
	echo "\t\t- Show this help dialog\n"; \
	\
	echo "\tall"; \
	echo "\t\t- Does nothing (same as invoking `tput bold`make`tput sgr0` with no"; \
	echo "\t\t  arguments)\n"; \
	\
	echo "\tinstall"; \
	echo "\t\t- Install `tput bold`$(PACKAGE)`tput sgr0` executable & data files onto"; \
	echo "\t\t  the system"; \
	echo "\t\t- Calls `tput bold`install-launcher`tput sgr0`, `tput bold`install-man`tput sgr0`,"; \
	echo "\t\t  & `tput bold`install-mime`tput sgr0`\n"; \
	\
	echo "\tuninstall"; \
	echo "\t\t- Remove all installed Debreate files from"; \
	echo "\t\t  the system"; \
	echo "\t\t- Calls `tput bold`uninstall-launcher`tput sgr0`, `tput bold`uninstall-mime`tput sgr0`,"; \
	echo "\t\t  & `tput bold`uninstall-mime`tput sgr0`\n"; \
	\
	echo "\tinstall-bitmaps"; \
	echo "\t\t- Install bitmaps used by application\n"; \
	\
	echo "\tuninstall-bitmaps"; \
	echo "\t\t- Remove bitmaps used by application\n"; \
	\
	echo "\tinstall-icons"; \
	echo "\t\t- Install icons for Debreate projects MimeType"; \
	echo "\t\t  registration\n"; \
	\
	echo "\tuninstall-icons"; \
	echo "\t\t- Remove Debreate MimeType icons\n"; \
	\
	echo "\tinstall-launcher"; \
	echo "\t\t- Install system menu launcher\n"; \
	\
	echo "\tuninstall-launcher"; \
	echo "\t\t- Remove system menu launcher\n"; \
	\
	echo "\tinstall-man"; \
	echo "\t\t- Install & compress Manpage file(s)\n"; \
	\
	echo "\tuninstall-man"; \
	echo "\t\t- Remove Debreate Manpage(s)\n"; \
	\
	echo "\tinstall-mime"; \
	echo "\t\t- Register MimeType information for Debreate"; \
	echo "\t\t  projects"; \
	echo "\t\t- Calls `tput bold`install-icons`tput sgr0`\n"; \
	\
	echo "\tuninstall-mime"; \
	echo "\t\t- Unregister Debreate project MimeType"; \
	echo "\t\t  information"; \
	echo "\t\t- Calls `tput bold`uninstall-icons`tput sgr0`\n"; \
	\
	echo "\tinstall-templates"; \
	echo "\t\t- Install template files used by application\n"; \
	\
	echo "\tuninstall-templates"; \
	echo "\t\t- Remove application template files\n"; \
	\
	echo "\tdist"; \
	echo "\t\t- Create a source distribution package\n"; \
	\
	echo "\tdistclean"; \
	echo "\t\t- Run `tput bold`clean`tput sgr0`, `tput bold`deb-clean`tput sgr0`, & delete compressed"; \
	echo "\t\t  distribution package archive\n"; \
	\
	echo "\tclean"; \
	echo "\t\t- Delete Debreate binary & any compiled Python"; \
	echo "\t\t  bytecode (.pyc) from the working directory\n"; \
	\
	echo "\tdebianize"; \
	echo "\t\t- Configure source for building a Debian package"; \
	echo "\t\t  (not necessary, should already be configured)"; \
	echo "\t\t- Uses `tput bold`dh_make`tput sgr0` command (apt install dh-make)\n"; \
	\
	echo "\tdeb-bin"; \
	echo "\t\t- Build a Debian (.deb) package for installation"; \
	echo "\t\t- Uses `tput bold`debuild`tput sgr0` command (apt install devscripts)\n"; \
	\
	echo "\tdeb-bin-signed"; \
	echo "\t\t- Build a Debian (.deb) package for installation"; \
	echo "\t\t  & sign the .changes file"; \
	echo "\t\t- Uses `tput bold`debuild`tput sgr0` command (apt install devscripts)\n"; \
	\
	echo "\tdeb-src"; \
	echo "\t\t- Create a source distribution package with"; \
	echo "\t\t  Debian .dsc, .build, & .changes files"; \
	echo "\t\t- Uses `tput bold`debuild`tput sgr0` command (apt install devscripts)\n"; \
	\
	echo "\tdeb-src-signed"; \
	echo "\t\t- Create a source distribution package & sign"; \
	echo "\t\t  the .changes file for upload to a repository"; \
	echo "\t\t- Uses `tput bold`debuild`tput sgr0` command (apt install devscripts)\n"; \
	\
	echo "\tdeb-clean"; \
	echo "\t\t- Delete files created by `tput bold`debuild`tput sgr0`\n"; \
	\
	echo "Environment Variables:"; \
	\
	echo "\tprefix"; \
	echo "\t\t- Target prefix under which files will be installed"; \
	echo "\t\t- Default is /usr/local\n"; \
	\
	echo "\tDESTDIR"; \
	echo "\t\t- Prepends a target directory to prefix"; \
	echo "\t\t- Files will be installed under DESTDIR\prefix"; \
	echo "\t\t- DESTDIR is not written to the `tput bold`$(PACKAGE)`tput sgr0`"; \
	echo "\t\t  executable so it will not be able to find the"; \
	echo "\t\t  `tput bold`init.py`tput sgr0` script"; \
	echo "\t\t- If used with `tput bold`uninstall`tput sgr0` it must match that of"; \
	echo "\t\t  the `tput bold`install`tput sgr0` invocation\n"; \
	\
	echo "Notes on Environment Variables:"; \
	\
	echo "\tCurrent Debreate does not use a build setup system (such as"; \
	echo "\tGNU Autotools or CMake), so the \"prefix\" variable is static."; \
	echo "\tThis means that when calling `tput bold`make uninstall`tput sgr0`, \"prefix\" must"; \
	echo "\tbe set to the same as it was for `tput bold`make install`tput sgr0`. The same goes"; \
	echo "\tfor the \"DESTDIR\" variable.\n"; \
	\
	echo "\tE.g. if `tput bold`make install prefix=/usr`tput sgr0` was called, then `tput bold`make"; \
	echo "\tuninstall prefix=/usr`tput sgr0` must be called to uninstall.\n"; \
