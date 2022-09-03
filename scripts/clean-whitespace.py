#!/usr/bin/env python3

import codecs, errno, os, sys

from scripts_globals import DIR_root
from scripts_globals import source_files


os.chdir(DIR_root)

for filename in source_files:
  if not os.path.isfile(filename):
    print("ERROR: source does not exist: {}".format(filename))
    sys.exit(errno.ENOENT)

  fin = codecs.open(filename, "r", encoding="utf-8")
  lines_orig = fin.read().replace("\r\n", "\n").replace("\r", "\n").split("\n")
  fin.close()

  lines_new = []
  for idx in range(len(lines_orig)):
    line = lines_orig[idx]
    while line.lstrip(" ").startswith("\t"):
      # replace leading tab with 2 spaces
      line = line.replace("\t", "  ", 1)

    while "#\t" in line:
      # replace comments with tabs
      line = line.replace("#\t", "#  ")

    line = line.rstrip()
    lines_new.append(line)

  if lines_new != lines_orig:
    print("Cleaning leading whitespace in {}".format(filename))

    fout = codecs.open(filename, "w", encoding="utf-8")
    fout.write("\n".join(lines_new))
    fout.close()
