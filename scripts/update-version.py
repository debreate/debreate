#!/usr/bin/env python

# MIT licensing
# See: docs/LICENSE.txt


import codecs, os, sys, errno
from scripts_globals import version_files, GetInfoValue


for F in version_files:
	if not os.path.isfile(version_files[F]):
		print("[ERROR] Required file not found: {}".format(version_files[F]))
		sys.exit(errno.ENOENT)


version = GetInfoValue("VERSION").split(".")
ver_maj = version[0]
ver_min = version[1]
ver_rev = 0
if len(version) > 2:
	ver_rev = version[2]
ver_dev = GetInfoValue("VERSION_dev")


def UpdateSingleLineFile(filename, testline, newvalue=".".join(version), suffix=""):
	fin = codecs.open(filename, "r", encoding="utf-8")
	lines_orig = fin.read().split("\n")
	fin.close()

	lines_new = list(lines_orig)

	for l in lines_new:
		l_index = lines_new.index(l)
		if l.strip(" ").startswith(testline):
			# Preserve whitespace
			ws = ""
			if l.startswith(" "):
				ws = l.split(testline)[0]

			lines_new[l_index] = "{}{}{}{}".format(ws, testline, newvalue, suffix)

			# Only change first instance
			break

	if lines_new != lines_orig:
		print("Writing new version information to {}".format(filename))

		fout = codecs.open(filename, "w", encoding="utf-8")
		fout.write("\n".join(lines_new))
		fout.close()


UpdateSingleLineFile(version_files["application"], "VERSION_maj = ", newvalue=ver_maj)
UpdateSingleLineFile(version_files["application"], "VERSION_min = ", newvalue=ver_min)
UpdateSingleLineFile(version_files["application"], "VERSION_rev = ", newvalue=ver_rev)
UpdateSingleLineFile(version_files["application"], "VERSION_dev = ", newvalue=ver_dev)
UpdateSingleLineFile(version_files["doxyfile"], "PROJECT_NUMBER		 = ")
UpdateSingleLineFile(version_files["locale"], "\"Project-Id-Version: Debreate ", suffix="\\n\"")
UpdateSingleLineFile(version_files["makefile"], "VERSION = ", newvalue=".".join(version))
