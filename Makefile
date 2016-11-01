# This is a generic Makefile. It will only work on systems with GNU make.

PACKAGE = debreate
VERSION = 0.7.11
BINDIR = bin
DATAROOT = share
DATADIR = $(DATAROOT)/$(PACKAGE)
APPSDIR = $(DATAROOT)/applications
PIXDIR = $(DATAROOT)/pixmaps

INSTALL_DATA = install -vm 0644
INSTALL_EXEC = install -vm 0755
INSTALL_FOLDER = cp -vR
MKDIR = mkdir -vp
UNINSTALL = rm -vf
UNINSTALL_FOLDER = rmdir -v --ignore-fail-on-non-empty

# This is written to 'prefix' in 'build' rule, then read in 'install'
prefix=/usr/local


FILES = \
	main.py \
	common.py \
	db_md5.py \
	db.py \
	language.py

FILES_EXECUTABLE = \
	init.py

FILES_WIZ_BIN = wiz_bin/*.py

FILES_DBR = dbr/*.py

FILES_GLOBALS = globals/*.py

FILES_EXTRA = \
	README.md \
	INFO \
	update-version.py

FILES_DOC = \
	docs/changelog \
	docs/LICENSE.txt \
	docs/release_notes \
	docs/usage.pdf

BITMAPS = \
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

DISTPACKAGE = $(PACKAGE)_$(VERSION).tar.xz

DISTDIRS = \
	bitmaps \
	dbr \
	data \
	docs \
	locale \
	debian \
	wiz_bin

DISTFILES = \
	$(FILES_EXECUTABLE) \
	$(FILES) \
	$(FILES_EXTRA) \
	Makefile

FILES_BUILD = \
	$(FILES) \
	$(FILES_DBR) \
	$(FILES_DOC) \
	$(FILES_EXECUTABLE) \
	$(FILES_EXTRA) \
	$(FILES_GLOBALS) \
	$(FILES_WIZ_BIN)


all:
	@echo "\n\tNothing to be done"; \
	echo "\trun one of the following:"; \
	echo "\n\t\t`tput bold`make install`tput sgr0` to install Debreate"; \
	echo "\t\t`tput bold`make help`tput sgr0`    to show a list of options\n"; \

install: build $(FILES_BUILD) $(BITMAPS) locale data/$(MENU)
	@exec=bin/$(PACKAGE); \
	if [ ! -f "$${exec}" ]; then \
		echo "\n\tERROR: ./bin/`tput bold`debreate`tput sgr0` executable not present\n"; \
		\
		echo "\t- Please run `tput bold`make`tput sgr0`, `tput bold`make build`tput sgr0`, or `tput bold`make all`tput sgr0`"; \
		echo "\t  to create it, then re-run `tput bold`make install`tput sgr0`\n"; \
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
		for py in $(FILES_EXECUTABLE); do \
			$(INSTALL_EXEC) "$${py}" "$${datadir}"; \
		done; \
		for py in $(FILES) $(EXTRA_FILES); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}"; \
		done; \
		\
		mkdir -vp "$${datadir}/dbr"; \
		for py in $(FILES_DBR); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}/dbr"; \
		done; \
		\
		mkdir -vp "$${datadir}/wiz_bin"; \
		for py in $(FILES_WIZ_BIN); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}/wiz_bin"; \
		done; \
		\
		mkdir -vp "$${datadir}/globals"; \
		for py in $(FILES_GLOBALS); do \
			$(INSTALL_DATA) "$${py}" "$${datadir}/globals"; \
		done; \
		\
		$(MKDIR) "$${datadir}/docs"; \
		for doc in $(FILES_DOC); do \
			$(INSTALL_DATA) "$${doc}" "$${datadir}/docs"; \
		done; \
		\
		mkdir -vp "$${datadir}/bitmaps"; \
		for png in $(BITMAPS); do \
			$(INSTALL_DATA) "$${png}" "$${datadir}/bitmaps"; \
		done; \
		\
		$(INSTALL_FOLDER) locale "$${datadir}"; \
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

uninstall:
	@target=$(DESTDIR)$(prefix); \
	bindir=$${target}/$(BINDIR); \
	datadir=$${target}/$(DATADIR); \
	appsdir=$${target}/$(APPSDIR); \
	pixdir=$${target}/$(PIXDIR); \
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

build: clean
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
	@dh_make -y -n -c mit -e antumdeluge@gmail.com -f "$(DISTPACKAGE)" -p "$(PACKAGE)_$(VERSION)" -i

clean:
	@find ./ -type f -name "*.pyc" -print -delete; \
	rm -vf "./bin/$(PACKAGE)"; \
	if [ -d "./bin" ]; then \
		$(UNINSTALL_FOLDER) "./bin"; \
	fi; \
	rm -vf "./prefix"; \

distclean: clean debuild-clean

debuild-clean:
	@rm -vrf "debian/debreate"
	@DEBUILD_FILES="\
	debian/debhelper-build-stamp debian/debreate.debhelper.log \
	debian/debreate.substvars debian/files"; \
	rm -vf $${DEBUILD_FILES};

dist: debuild-clean
	@echo "Creating distribution package ..."
	@if [ -f "$(DISTPACKAGE)" ]; then \
		rm -v "$(DISTPACKAGE)"; \
	fi
	@tar -cJf "$(DISTPACKAGE)" $(DISTFILES) $(DISTDIRS)
	@file "$(DISTPACKAGE)"

help:
	echo "Usage:"; \
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
