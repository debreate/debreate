
LOCDEST=${DEBDEST}/locale

LOCALES= \
	ar \
	es \
	fr \
	it \
	ru

install:
	@echo
	@install -v -d ${LOCDEST}
	@install -v -m 0644 ${PNAME}.pot ${LOCDEST}
	@for loc in ${LOCALES}; do \
		install -v -d ${LOCDEST}/$${loc}/LC_MESSAGES; \
		install -v -m 0644 $${loc}/${PNAME}.po ${LOCDEST}/$${loc}; \
		install -v -m 0644 $${loc}/LC_MESSAGES/${PNAME}.mo \
			${LOCDEST}/$${loc}/LC_MESSAGES/${PNAME}.mo; \
		done
	
uninstall:
	@echo
	@#for loc in ${LOCALES}; do \
		rm -vf ${LOCDEST}/$${loc}/LC_MESSAGES/${PNAME}.mo \
			${LOCDEST}/$${loc}/${PNAME}.po; \
		rmdir -vp ${LOCDEST}/$${loc}/LC_MESSAGES; \
		done
	@rm -vf ${LOCDEST}/${PNAME}.pot
	@# NOTE: Should use "rmdir -vp" here?
	@rm -vr ${LOCDEST}
	
	@echo
	@echo "‣‣ DONE"
	