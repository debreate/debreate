#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ([2.69])
AC_INIT([debreate], [0.7.10], [antumdeluge@gmail.com])

# Checks for programs.
#AC_PROG_INSTALL
#AC_PROG_MAKE_SET

AC_ARG_VAR(PYTHON, The Python interpreter)

# Checks for Python interpreter
if ! test ${PYTHON}; then
	PYTHON=python2
fi

AC_CHECK_PROG(PYTHON_CHECK, ${PYTHON}, yes)
if test x"${PYTHON_CHECK}" != x"yes"; then
	AC_CHECK_PROG(PYTHON_CHECK, python, yes)
	if test x"${PYTHON_CHECK}" != x"yes"; then
	    AC_MSG_ERROR([Required python interpreter not found])
	else
		PYTHON=python
	fi
fi

# Macro to check Python version
AC_DEFUN([AC_PYTHON_VERSION],
	[AC_MSG_CHECKING(for Python version ${PY_REQ_MAJ}.${PY_REQ_MIN})
	PY_REQ_MAJ=2
	PY_REQ_MIN=7
	PY_VERSION=`python --version 2>&1 | cut -d' ' -f2`
	AC_MSG_RESULT(${PY_VERSION})
	if test `echo ${PY_VERSION} | cut -d. -f1` -ne ${PY_REQ_MAJ}; then
		AC_MSG_ERROR(Required Python version not found)
	elif ! test `echo ${PY_VERSION} | cut -d. -f2` -ge ${PY_REQ_MIN}; then
		AC_MSG_ERROR(Required Python version not found)
	fi
])

# Macro to check for Python module
AC_DEFUN([AC_PYTHON_MODULE],
	[AC_MSG_CHECKING(for module $1 in ${PYTHON})
	echo "import $1" | ${PYTHON} -
	if test $? -ne 0; then
		AC_MSG_RESULT(not found)
		AC_MSG_ERROR(You need the module $1 available to python for this package)
	fi
	AC_MSG_RESULT(found)
])

AC_PYTHON_VERSION()
AC_PYTHON_MODULE([wx])

AC_CONFIG_FILES([Makefile
                 src/Makefile
                 src/locale/Makefile])
AC_OUTPUT
