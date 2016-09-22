# This is a generic Makefile. It will only work on systems with GNU make.

PACKAGE = debreate
VERSION = 0.7.11
BINDIR = bin
DATAROOT = share
DATADIR = $(DATAROOT)/$(PACKAGE)
APPSDIR = $(DATAROOT)/applications
PIXDIR = $(DATAROOT)/pixmaps
DOCDIR = $(DATAROOT)/doc/$(PACKAGE)

INSTALL_DATA = install -vm 0644
INSTALL_EXEC = install -vm 0755
INSTALL_FOLDER = cp -vR
MKDIR = mkdir -vp
UNINSTALL = rm -vf
UNINSTALL_FOLDER = rmdir -v --ignore-fail-on-non-empty

# This is written to 'prefix' in 'build' rule, then read in 'install'
prefix=/usr/local


FILES_executable = \
	init.py

FILES_root = \
	main.py

FILES_wiz_bin = \
	wiz_bin/__init__.py \
	wiz_bin/build.py \
	wiz_bin/clog.py \
	wiz_bin/control.py \
	wiz_bin/copyright.py \
	wiz_bin/depends.py \
	wiz_bin/files.py \
	wiz_bin/greeting.py \
	wiz_bin/menu.py \
	wiz_bin/scripts.py

FILES_wiz_src = \
	wiz_src/__init__.py \
	wiz_src/control.py

FILES_dbr = \
	dbr/__init__.py \
	dbr/about.py \
	dbr/buttons.py \
	dbr/charctrl.py \
	dbr/constants.py \
	dbr/custom.py \
	dbr/functions.py \
	dbr/language.py \
	dbr/log.py \
	dbr/md5.py \
	dbr/message.py \
	dbr/pathctrl.py \
	dbr/templates.py \
	dbr/wizard.py

FILES_doc = \
	docs/BUGS.txt \
	docs/changelog \
	docs/LICENSE.txt \
	docs/release_notes \
	docs/TODO.txt \
	docs/usage.pdf

FILES_bitmap = \
	bitmaps/add32.png \
	bitmaps/browse32.png \
	bitmaps/browse64.png \
	bitmaps/build32.png \
	bitmaps/build64.png \
	bitmaps/cancel32.png \
	bitmaps/clear32.png \
	bitmaps/clock16.png \
	bitmaps/confirm32.png \
	bitmaps/debreate64.png \
	bitmaps/del32.png \
	bitmaps/error64.png \
	bitmaps/exit32.png \
	bitmaps/globe16.png \
	bitmaps/import32.png \
	bitmaps/next32.png \
	bitmaps/pipe32.png \
	bitmaps/prev32.png \
	bitmaps/preview32.png \
	bitmaps/preview64.png \
	bitmaps/question64.png \
	bitmaps/save32.png \
	bitmaps/save64.png

MENU = debreate.desktop

FILES_data = \
	data/$(MENU)

FILES_build = \
	$(FILES_executable) \
	$(FILES_root) \
	$(FILES_wiz_bin) \
	$(FILES_wiz_src) \
	$(FILES_dbr) \
	$(FILES_doc) \
	$(FILES_bitmap) \
	$(FILES_data)

FILES_dist = \
	$(FILES_executable) \
	$(FILES_root) \
	$(FILES_data) \
	INFO \
	Makefile \
	README.md \
	test.sh \
	update-version.py

DIRS_build = \
	locale \
	templates

DIRS_dist = \
	$(DIRS_build) \
	bitmaps \
	dbr \
	debian \
	docs \
	wiz_bin \
	wiz_src

PACKAGE_dist = $(PACKAGE)_$(VERSION).tar.xz

DOXYGEN_CONFIG = docs/Doxyfile


all:
	@echo "\n\tNothing to be done"; \
	echo "\trun one of the following:"; \
	echo "\n\t\t`tput bold`make install`tput sgr0` to install Debreate"; \
	echo "\t\t`tput bold`make help`tput sgr0`    to show a list of options\n"; \

install: build $(FILES_executable) $(FILES_root) $(FILES_wiz_bin) $(FILES_wiz_src) $(FILES_dbr) $(FILES_bitmap) $(FILES_data) $(DIRS_build) install-doc
	@exec=bin/$(PACKAGE); \
	if [ ! -f "$${exec}" ]; then \
		echo "\n\tERROR: ./bin/`tput bold`debreate`tput sgr0` executable not present\n"; \
		\
		echo "\t- Please run `tput bold`make`tput sgr0`, `tput bold`make build`tput sgr0`, or `tput bold`make all`tput sgr0`"; \
		echo "\t  to create it, then re-run `tput bold`make install`tput sgr0`\n"; \
		exit 1; \
	\
	else \
		target=$(DESTDIR)$(prefix); \
		bindir=$${target}/$(BINDIR); \
		datadir=$${target}/$(DATADIR); \
		appsdir=$${target}/$(APPSDIR); \
		pixdir=$${target}/$(PIXDIR); \
		\
		echo "\nprefix set to $(prefix)"; \
		echo "Install target set to $${target}\n"; \
		\
		mkdir -vp "$${target}/$(DATADIR)"; \
		for py in $(FILES_executable); do \
			$(INSTALL_EXEC) "$${py}" "$${datadir}"; \
		done; \
		for py in $(FILES_root); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}"; \
		done; \
		\
		mkdir -vp "$${datadir}/dbr"; \
		for py in $(FILES_dbr); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}/dbr"; \
		done; \
		\
		$(MKDIR) "$${datadir}/wiz_bin"; \
		for py in $(FILES_wiz_bin); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}/wiz_bin"; \
		done; \
		\
		$(MKDIR) "$${datadir}/wiz_src"; \
		for py in $(FILES_wiz_src); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}/wiz_src"; \
		done; \
		\
		mkdir -vp "$${datadir}/bitmaps"; \
		for png in $(FILES_bitmap); do \
			$(INSTALL_DATA) "$${png}" "$${datadir}/bitmaps"; \
		done; \
		\
		for d in $(DIRS_build); do \
			$(INSTALL_FOLDER) "$${d}" "$${datadir}"; \
		done; \
		\
		$(MKDIR) "$${bindir}"; \
		$(INSTALL_EXEC) "$${exec}" "$${bindir}"; \
		\
		$(MKDIR) "$${pixdir}"; \
		$(INSTALL_DATA) "bitmaps/debreate64.png" "$${pixdir}/debreate.png"; \
		\
		$(MKDIR) "$${appsdir}"; \
		$(INSTALL_EXEC) "data/$(MENU)" "$${appsdir}"; \
	\
	fi; \
	\
	# If source code was modified, restore original; \
	dbr_about="./dbr/about.py"; \
	if [ -f "$${dbr_about}.orig" ]; then \
		echo "\nRestoring original source: $${dbr_about} ..."; \
		mv -vf "$${dbr_about}.orig" "$${dbr_about}"; \
	fi; \
	\
	echo "\nInstallation complete"; \

install-doc: $(FILES_doc)
	@docdir="$(prefix)/$(DOCDIR)"; \
	target="$(DESTDIR)$${docdir}"; \
	\
	echo "\nInstalling documentation ..."; \
	mkdir -vp "$${target}"; \
	for doc in $(FILES_doc); do \
		$(INSTALL_DATA) "$${doc}" "$${target}"; \
	done; \
	\
	#echo "\nCompressing changelog ..."; \
	#gzip -vf9 "$${target}/changelog"; \
	\
	src_about="dbr/about.py"; \
	echo "Configuring source for new changelog location ..."; \
	log_old_line="CHANGELOG = u'{}/docs/changelog'.format(dbr.application_path)"; \
	log_new_line="CHANGELOG = u'$${docdir}/changelog'"; \
	sed -i.orig -e "s|$${log_old_line}|$${log_new_line}|" "$${src_about}"; \
	\
	echo "Configuring source for new LICENSE.txt location ..."; \
	lic_old_line="LICENSE = u'{}/docs/LICENSE.txt'.format(dbr.application_path)"; \
	lic_new_line="LICENSE = u'$${docdir}/LICENSE.txt'"; \
	sed -i -e "s|$${lic_old_line}|$${lic_new_line}|" "$${src_about}"; \

uninstall:
	@target=$(DESTDIR)$(prefix); \
	bindir=$${target}/$(BINDIR); \
	datadir=$${target}/$(DATADIR); \
	appsdir=$${target}/$(APPSDIR); \
	pixdir=$${target}/$(PIXDIR); \
	docdir=$${target}/$(DOCDIR); \
	\
	echo "\nprefix set to $(prefix)"; \
	echo "Uninstall target set to $${target}\n"; \
	\
	$(UNINSTALL) "$${appsdir}/$(MENU)"; \
	$(UNINSTALL) "$${pixdir}/debreate.png"; \
	$(UNINSTALL) "$${bindir}/$(PACKAGE)"; \
	\
	if [ -d "$${datadir}" ]; then \
		for f in `find "$${datadir}" -type f`; do \
			$(UNINSTALL) "$${f}"; \
		done; \
		find "$${datadir}" -type d -empty -delete; \
	fi; \
	\
	if [ -d "$${docdir}" ]; then \
		for f in `find "$${docdir}" -type f`; do \
			$(UNINSTALL) "$${f}"; \
		done; \
		find "$${docdir}" -type d -empty -delete; \
	fi; \

build:
	@exec=bin/$(PACKAGE); \
	echo "\nprefix set to \"$(prefix)\""; \
	\
	exec_script=\#"!/bin/sh \n\n$(prefix)/$(DATAROOT)/$(PACKAGE)/init.py"; \
	\
	mkdir -vp "bin"; \
	echo "Creating executable \"$${exec}\" ..."; \
	echo "$${exec_script}\n" > "$${exec}"; \
	\
	echo "\nBuild complete. Now execute `tput bold`make install`tput sgr0`.\n"; \

debuild:
	@debuild -b -uc -us

debuild-source:
	@debuild -S -uc -us

debuild-signed:
	@debuild -S -sa

debianize: dist
	@dh_make -y -n -c mit -e antumdeluge@gmail.com -f "$(PACKAGE_dist)" -p "$(PACKAGE)_$(VERSION)" -i

doc-html: $(DOXYGEN_CONFIG)
	@doxygen "$(DOXYGEN_CONFIG)"; \
	echo "\nOptimizing Doxygen HTML docs for Python ...\n"; \
	find docs/doxygen -type f -exec sed -i -e 's/def //' {} +; \
	find docs/doxygen -type f -exec sed -i -e 's/def&#160;//' {} +; \
	find docs/doxygen -type f -exec sed -i -e 's/class &#160;//' {} +; \
	\
	# Removes whitespace before parameters \
	find docs/doxygen -type f -exec sed -i -e '/<td class="paramtype">/c\' {} +; \

clean: doc-clean
	@find ./ -type f -name "*.pyc" -print -delete; \
	rm -vf "./bin/$(PACKAGE)"; \
	if [ -d "./bin" ]; then \
		$(UNINSTALL_FOLDER) "./bin"; \
	fi; \
	rm -vf "./prefix"; \

distclean: clean debuild-clean
	@echo "Cleaning distribution ..."; \
	rm -vf "$(PACKAGE_dist)";

debuild-clean:
	@rm -vrf "debian/debreate"
	@DEBUILD_FILES="\
	debian/debhelper-build-stamp debian/debreate.debhelper.log \
	debian/debreate.substvars debian/files"; \
	rm -vf $${DEBUILD_FILES};

doc-clean:
	@rm -vrf docs/doxygen

dist: debuild-clean $(FILES_dist) $(DIRS_dist)
	@echo "Creating distribution package ..."; \
	if [ -f "$(PACKAGE_dist)" ]; then \
		rm -v "$(PACKAGE_dist)"; \
	fi; \
	tar -cJf "$(PACKAGE_dist)" $(FILES_dist) $(DIRS_dist); \
	file "$(PACKAGE_dist)"; \

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
	echo "\tall|build"; \
	echo "\t\t- Create `tput bold`debreate`tput sgr0` executable (same as invoking"; \
	echo "\t\t  `tput bold`make`tput sgr0` with no arguments)\n"; \
	\
	echo "\tinstall"; \
	echo "\t\t- Install `tput bold`debreate`tput sgr0` executable & data files onto"; \
	echo "\t\t  the system\n"; \
	\
	echo "\tuninstall"; \
	echo "\t\t- Remove all installed Debreate files from"; \
	echo "\t\t  the system\n"; \
	\
	echo "\tdoc-html"; \
	echo "\t\t- Build Doxygen HTML files in docs/doxygen"; \
	echo "\t\t- Requires `tput bold`doxygen`tput sgr0` command (apt install doxygen)\n"; \
	\
	echo "\tdist"; \
	echo "\t\t- Create a source distribution package\n"; \
	\
	echo "\tdebianize"; \
	echo "\t\t- Configure source for building a Debian package"; \
	echo "\t\t  (not necessary, should already be configured)"; \
	echo "\t\t- Uses `tput bold`dh_make`tput sgr0` command (apt install dh-make)\n"; \
	\
	echo "\tdebuild"; \
	echo "\t\t- Build a Debian (.deb) package for installation"; \
	echo "\t\t- Uses `tput bold`debuild`tput sgr0` command (apt install devscripts)\n"; \
	\
	echo "\tdebuild-source"; \
	echo "\t\t- Create a source distribution package with"; \
	echo "\t\t  Debian .dsc, .build, & .changes files\n"; \
	\
	echo "\tdebuild-signed"; \
	echo "\t\t- Create a source distribution package & sign"; \
	echo "\t\t  it for upload to a repository\n"; \
	\
	echo "\tclean"; \
	echo "\t\t- Delete Debreate binary & any compiled Python"; \
	echo "\t\t  bytecode (.pyc) from the working directory\n"; \
	\
	echo "\tdoc-clean"; \
	echo "\t\t- Delete Doxygen HTML files from docs/doxygen.\n"; \
	\
	echo "\tdebuild-clean"; \
	echo "\t\t- Delete files create by `tput bold`debuild`tput sgr0`\n"; \
	\
	echo "\tdistclean"; \
	echo "\t\t- Run `tput bold`clean`tput sgr0` & `tput bold`debuild-clean`tput sgr0`\n"; \
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
	echo "\t\t- DESTDIR is not written to the `tput bold`debreate`tput sgr0`"; \
	echo "\t\t  executable so it will not be able to find the"; \
	echo "\t\t  `tput bold`init.py`tput sgr0` script"; \
	echo "\t\t- If used with `tput bold`uninstall`tput sgr0` it must match that of"; \
	echo "\t\t  the `tput bold`install`tput sgr0` invocation\n"; \
