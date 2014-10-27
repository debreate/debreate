
# Sub-directories
DB=db
DOC=docs
LOC=locale
PIX=bitmaps
MKDIRS= \
	${DEBDEST}/${DB} \
	${DEBDEST}/${DOC} \
	${DEBDEST}/${PIX} \
	${BINDIR}

# Base Files #
EXE=launch.py
FILES= \
	common.py \
	db_md5.py \
	db.py \
	debreate.py \
	language.py \
	panbuild.py \
	panclog.py \
	pancontrol.py \
	pancopyright.py \
	pandepends.py \
	panfiles.py \
	paninfo.py \
	panmenu.py \
	panscripts.py

DB_FILES= \
	${DB}/dbabout.py \
	${DB}/dbbuttons.py \
	${DB}/dbcharctrl.py \
	${DB}/dbmessage.py \
	${DB}/dbpathctrl.py \
	${DB}/dbwizard.py

DOC_FILES= \
	${DOC}/changelog \
	${DOC}/gpl-3.0.txt \
	${DOC}/release_notes \
	${DOC}/usage.pdf

PIX_FILES= \
	${PIX}/add32.png \
	${PIX}/browse32.png \
	${PIX}/browse64.png \
	${PIX}/build32.png \
	${PIX}/build64.png \
	${PIX}/cancel32.png \
	${PIX}/clear32.png \
	${PIX}/clock16.png \
	${PIX}/confirm32.png \
	${PIX}/debreate64.png \
	${PIX}/del32.png \
	${PIX}/error64.png \
	${PIX}/exit32.png \
	${PIX}/globe16.png \
	${PIX}/import32.png \
	${PIX}/next32.png \
	${PIX}/pipe32.png \
	${PIX}/prev32.png \
	${PIX}/preview32.png \
	${PIX}/preview64.png \
	${PIX}/question64.png \
	${PIX}/save32.png \
	${PIX}/save64.png

install: ${EXE} ${FILES} ${DB_FILES} ${DOC_FILES} ${PIX_FILES}
	@echo
	
	@cd ${LOC}; \
		echo "‣‣ Making \"install\" in `pwd`"; \
		make install PREFIX=${PREFIX} DESTDIR=${DESTDIR} DEBDEST=${DEBDEST} \
			PNAME=${PNAME}; \
		echo; \
		echo "‣‣ DONE"; \
		echo; \
		echo "‣‣ Leaving directory `pwd`"
	
	@echo
	@install -v -d ${MKDIRS}
	@install -v ${EXE} ${DEBDEST}
	@install -v -l s ${DEBDEST}/${EXE} ${BINDIR}/${PNAME}
	
	@for f in ${FILES}; do \
		install -v -m 0644 $${f} ${DEBDEST}; \
		done
	
	@for f in ${DB_FILES}; do \
		install -v -m 0644 $${f} ${DEBDEST}/${DB}; \
		done
	
	@for f in ${DOC_FILES}; do \
		install -v -m 0644 $${f} ${DEBDEST}/${DOC}; \
		done
	
	@for f in ${PIX_FILES}; do \
		install -v -m 0644 $${f} ${DEBDEST}/${PIX}; \
		done
	
uninstall:
	@echo
	
	@cd ${LOC}; \
		echo "‣‣ Making \"uninstall\" in `pwd`"; \
		make uninstall PREFIX=${PREFIX} DESTDIR=${DESTDIR} DEBDEST=${DEBDEST} \
			PNAME=${PNAME} BINDIR=${BINDIR}; \
		echo; \
		echo "‣‣ DONE"; \
		echo; \
		echo "‣‣ Leaving directory `pwd`"
	
	@echo
	@for f in ${PIX_FILES}; do \
		rm -vf ${DEBDEST}/$${f}; \
		done
	@# NOTE: Should use "rmdir -vp" here?
	@rm -vr ${DEBDEST}/${PIX}
	
	@for f in ${DOC_FILES}; do \
		rm -vf ${DEBDEST}/$${f}; \
		done
	@# NOTE: Should use "rmdir -vp" here?
	@rm -vr ${DEBDEST}/${DOC}
	
	@for f in ${DB_FILES}; do \
		rm -vf ${DEBDEST}/$${f}; \
		done
	@# NOTE: Should use "rmdir -vp" here?
	@rm -vr ${DEBDEST}/${DB}
	
	@for f in ${FILES}; do \
		rm -vf ${DEBDEST}/$${f}; \
		done
	
	@unlink ${BINDIR}/${PNAME}
	@rm -vf ${DEBDEST}/${EXE}
	@# NOTE: Should use "rmdir -vp" here?
	@rm -vr ${DEBDEST}
	
	@echo
	@echo "‣‣ DONE"
	