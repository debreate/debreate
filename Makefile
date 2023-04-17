#!/usr/bin/env make

# This generic GNU Makefile is a wrapper for the build.py Python script.

all:
	@echo "\n\n\tNothing to be done"; \
	echo "\trun one of the following:"; \
	echo "\n\t\t`tput bold`make install`tput sgr0` to install Debreate"; \
	echo "\t\t`tput bold`make help`tput sgr0`    to show a list of options\n"; \

stage:
	@python3 build.py -t stage

install:
	@python3 build.py -t install -d "$(DESTDIR)" -p "$(prefix)"

uninstall:
	@python3 build.py -t uninstall -d "$(DESTDIR)" -p "$(prefix)"

dist-source:
	@python3 build.py -t dist-source

dist: dist-source

dist-bin:
	@python3 build.py -t dist-bin

dist-deb:
	@python3 build.py -t dist-deb

dist-deb-signed:
	@#debuild -b -sa \
	echo "dist-deb-signed: feature not available"

dist-deb-src:
	@#debuild -S -uc -us \
	echo "dist-deb-src: feature not available"

deb-source:
	@python3 build.py -t deb-source

debianize: dist
	@#dh_make -y -n -c mit -e antumdeluge@gmail.com -f "$(PACKAGE_dist)" -p "$(PACKAGE)_$(VERSION)" -i \
	echo "debianize: feature not available"

doxygen:
	@python3 build.py -t docs

doxygen-format: docs
	@#./scripts/doxygen-format.py \
	echo "doxygen-format: feature not available"

clean:
	@python3 build.py -t clean

clean-stage:
	@python3 build.py -t clean-stage

clean-deb:
	@python3 build.py -t clean-deb

clean-dist:
	@python3 build.py -t clean-dist

# NOTE: `distclean` must not call `clean-deb`
distclean: clean-dist

update-version:
	@python3 build.py -t update-version

test:
	@python3 build.py -t test

check-code:
	@python3 build.py -t check-code

changes:
	@python3 build.py -t changes

changes-deb:
	@python3 build.py -t changes-deb

help:
	@echo "Usage:"; \
	\
	echo "\tmake [command]\n"; \
	\
	echo "Commands:"; \
	\
	echo "\thelp"; \
	echo "\t\t- Show help information.\n"; \
	\
	echo "\tall"; \
	echo "\t\t- Does nothing (same as invoking `tput bold`make`tput sgr0` with no arguments).\n"; \
	\
	echo "\tstage"; \
	echo "\t\t- Prepare files for installation or distribution.\n"; \
	\
	echo "\tinstall"; \
	echo "\t\t- Install files to directory specified by `tput bold`prefix`tput sgr0` environment variable.\n"; \
	\
	echo "\tuninstall"; \
	echo "\t\t- Uninstall files from directory specified by `tput bold`prefix`tput sgr0` environment variable.\n"; \
	\
	echo "\tdist-source|dist"; \
	echo "\t\t- Build a source distribution package.\n"; \
	\
	echo "\tdist-bin"; \
	echo "\t\t- Build a portable binary .zip distribution package.\n"; \
	\
	echo "\tdist-deb"; \
	echo "\t\t- Build a binary Debian distribution package."; \
	echo "\t\t- Requires `tput bold`debuild`tput sgr0` (apt install devscripts).\n"; \
	\
	echo "\tdeb-source"; \
	echo "\t\t- Build a signed Debian source package for uploading to repo or PPA.\n"; \
	\
	echo "\tdoxygen"; \
	echo "\t\t- Build documentation using `tput bold`Doxygen`tput sgr0`.\n"; \
	\
	echo "\tclean"; \
	echo "\t\t- Remove all temporary build files.\n"; \
	\
	echo "\tclean-stage"; \
	echo "\t\t- Remove temporary build files from 'build/stage' directory.\n"; \
	\
	echo "\tclean-deb"; \
	echo "\t\t- Remove temporary build files from 'debian' directory.\n"; \
	\
	echo "\tclean-dist"; \
	echo "\t\t- Remove built packages from 'build/dist' directory.\n"; \
	\
	echo "\tupdate-version"; \
	echo "\t\t- Update relevant files with version information from 'build.conf'.\n"; \
	\
	echo "\ttest"; \
	echo "\t\t- Run configured unit tests from 'tests' directory.\n"; \
	\
	echo "\tcheck-code"; \
	echo "\t\t- Check code with pylint & mypy.\n"; \
	\
	echo "\tchanges"; \
	echo "\t\t- Print most recent changes from 'doc/changelog' to stdout.\n"; \
	\
	echo "\tchanges-deb"; \
	echo "\t\t- Print most recent changes from'doc/changelog' in Debianized format to stdout.\n"; \
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
	echo "\t\t- DESTDIR is not written to the `tput bold`$(PACKAGE)`tput sgr0`executable so"; \
	echo "\t\t  it will not be able to find the `tput bold`init.py`tput sgr0` script"; \
	echo "\t\t- If used with `tput bold`uninstall`tput sgr0` it must match that of"; \
	echo "\t\t  the `tput bold`install`tput sgr0` invocation\n"; \
	\
	echo "Notes on Environment Variables:"; \
	\
	echo "\tDebreate does not use a build setup system (such as GNU"; \
	echo "\tAutotools or CMake), so the \"prefix\" variable is static."; \
	echo "\tThis means that when calling `tput bold`make uninstall`tput sgr0`, \"prefix\""; \
	echo "\tmust be set to the same as it was for `tput bold`make install`tput sgr0`. The"; \
	echo "\tsame goes for the \"DESTDIR\" variable.\n"; \
	\
	echo "\tE.g. if `tput bold`make install prefix=/usr`tput sgr0` was called, then `tput bold`make"; \
	echo "\tuninstall prefix=/usr`tput sgr0` must be called to uninstall.\n"; \
