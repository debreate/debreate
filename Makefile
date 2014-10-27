MAKE=make

### Project ###

PNAME=debreate
PNAME_T=Debreate
VER_MAJ=0
VER_MIN=7
VER_REL=11
VERSION=${VER_MAJ}.${VER_MIN}.${VER_REL}

### Environment ###

PREFIX=/usr/local
DESTDIR=${PREFIX}
BINDIR=${DESTDIR}/bin
INCLDIR=${DESTDIR}/include
LIBDIR=${DESTDIR}/lib

### Installation ###

# Base Directories #
DATA=data
SRC=src
DB=db
DB_SRC=${SRC}/${DB}
PIX=bitmaps
PIX_SRC=${SRC}/${PIX}
DOC=docs
DOC_SRC=${SRC}/${DOC}
LOC=locale
LOC_SRC=${SRC}/${LOC}

# Data Files #
ICON=${DATA}/pixmap/debreate.png

# Destination Directories #
DEBDEST=${DESTDIR}/share/debreate
APPSDEST=${DESTDIR}/share/applications
PIXDEST=${DESTDIR}/share/pixmaps

help:
	@echo
	@echo "‣ Debreate is written in the Python interpreted language. It"
	@echo "  does not need to be compiled. To install execute the"
	@echo "  following:"
	@echo
	@echo "		make install"
	@echo
	@echo "‣ This makefile uses the default prefix \"/usr/local\". To"
	@echo "  install to a different location use the PREFIX option:"
	@echo
	@echo "		make install PREFIX=<path>"
	@echo
	@echo "‣ Alternatively you can use the DESTDIR option:"
	@echo
	@echo "		make install DESTDIR=<path>"
	@echo
	@echo "‣ Currently these are interchangeable but in the future they"
	@echo "  may have separate functions."
	@echo
	@echo "‣ WARNING: DESTDIR must be declared the same for uninstall"
	@echo "  as declared for install."
	@echo
	@echo "		make uninstall DESTDIR=<path>"
	@echo
	
tests:
	@echo
	@echo "‣‣ Making \"tests\" in `pwd`"
	@echo "Need instructions to test for python version, wxpython \
	(wxversion), dpkg, fakeroot, & coreutils (chmod)."
	
install: tests src/${EXE} ${FILES} ${DB_FILES} ${PIX_FILES} ${DOC_FILES} \
         ${LOC_FILES} ${ICON}
	@echo
	@echo "‣‣ Installing Debreate to ${DESTDIR}/share/debreate"
	@echo
	
	@cd src; \
		echo "‣‣ Making \"install\" in `pwd`"; \
		make install PREFIX=${PREFIX} DESTDIR=${DESTDIR} DEBDEST=${DEBDEST} \
			PNAME=${PNAME} BINDIR=${BINDIR}; \
		echo; \
		echo "‣‣ DONE"; \
		echo; \
		echo "‣‣ Leaving directory `pwd`"
	
	@echo
	@echo "‣‣ Making \"install\" in `pwd`"
	@echo
	@install -v -d ${APPSDEST} ${PIXDEST}
	@install -v -m 0644 ${ICON} ${PIXDEST}
	@install -v -m 0644 ${PNAME}.desktop ${APPSDEST}
	@echo
	@echo "‣‣ DONE"
	@echo
	
uninstall:
	@echo
	@echo "Uninstalling Debreate from ${DEBDEST}"
	@echo
	
	@cd src; \
		echo "‣‣ Making \"uninstall\" in `pwd`"; \
		make uninstall PREFIX=${PREFIX} DESTDIR=${DESTDIR} DEBDEST=${DEBDEST} \
			PNAME=${PNAME} BINDIR=${BINDIR}; \
		echo; \
		echo "‣‣ DONE"; \
		echo; \
		echo "‣‣ Leaving directory `pwd`"
	
	@echo
	@echo "‣‣ Making \"uninstall\" in `pwd`"
	@echo
	@rm -vf ${APPSDEST}/${PNAME}.desktop ${PIXDEST}/${PNAME}.png
	@echo
	@echo "‣‣ DONE"
	@echo
	