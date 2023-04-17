#! /usr/bin/env python3

# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @script update-locale.py

import errno
import os
import re
import subprocess
import sys
import time

path_script = os.path.realpath(sys.argv[0])
dir_scripts = os.path.dirname(path_script)
dir_app = os.path.dirname(dir_scripts)

sys.path.insert(0, os.path.join(dir_app, "lib"))

from libdbr import config
from libdbr import fileio
from libdbr import paths


def parseStrings():
  os.chdir(dir_app)

  cmd_xgettext = paths.getExecutable("xgettext")
  if not cmd_xgettext:
    sys.stderr.write("ERROR: 'xgettext' not found\n")
    exit(errno.ENOENT)

  file_config = paths.join(dir_app, "build.conf")
  cfg = config.add("build", file_config)

  files_source = [paths.join(dir_app, cfg.getValue("executable"))]
  for _dir in cfg.getList("dirs_app", sep=";"):
    _dir = paths.join(dir_app, _dir)
    if not os.path.isdir(_dir):
      continue
    for ROOT, DIRS, FILES in os.walk(_dir):
      for f in FILES:
        if not f.endswith(".py"):
          continue
        files_source.append(paths.join(ROOT, f))

  dir_locale = paths.join(dir_app, 'locale')
  if not os.path.isdir(dir_locale):
    sys.stderr.write("ERROR: locale directory does not exist: {}\n".format(dir_locale))
    exit(errno.ENOENT)

  file_pot = paths.join(dir_locale, 'debreate.pot')
  deb_info = cfg.getKeyedValue("deb_info", sep=";")
  version = cfg.getValue("version")
  version_dev = int(cfg.getValue("version_dev"))
  if version_dev > 0:
    version += "dev{}".format(version_dev)

  params = [
    "--language=Python",
    # parse 'GT' keyword & don't use default keywords
    "--keyword=GT", "-k",
    "--package-name={}".format(cfg.getValue("package").title()),
    "--package-version={}".format(version),
    "--copyright-holder={}".format(deb_info["author"]),
    "--msgid-bugs-address={}".format(deb_info["email"]),
    # style
    "--indent", "--sort-output", "--no-location", "--no-wrap", #"--omit-header",
    # write to stdout
    "--output=-"
  ]

  # get translatable strings
  res = subprocess.run([cmd_xgettext] + params + files_source, stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT)
  if res.returncode != 0:
    sys.stderr.write("subprocess returned error:\n\n{}\n".format(res.stdout.decode("utf-8")))
    exit(res.returncode)

  t_strings = res.stdout.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").split("\n")
  t_strings.insert(5, \
"\
# NOTES:\n\
#   If \"%s\" or \"{}\" is in the msgid, be sure to put it in\n\
#   the msgstr or parts of Debreate will not function.\n\
#\n\
#   If you do not wish to translate a line just leave its\n\
#   msgstr blank\
")

  content_old = ""
  if os.path.isfile(file_pot):
    content_old = fileio.readFile(file_pot)

  content_new = "\n".join(t_strings)
  content_new = re.sub("SOME DESCRIPTIVE TITLE.", "Debreate - Debian Package Builder", content_new,
      count=1)
  content_new = re.sub("\(C\) YEAR", "© 2014-{}".format(time.strftime('%Y')), content_new, count=1)
  if content_new != content_old:
    fileio.writeFile(file_pot, content_new)
    print("updated translatable strings '{}'".format(file_pot))
  else:
    print("translatable strings unchanged '{}'".format(file_pot))

def updateTranslations():
  cmd_msgmerge = paths.getExecutable("msgmerge")
  if not cmd_msgmerge:
    sys.stderr.write("ERROR: 'msgmerge' not found\n")
    exit(errno.ENOENT)

  dir_locale = paths.join(dir_app, 'locale')
  file_template = paths.join(dir_locale, "debreate.pot")
  if not os.path.isfile(file_template):
    sys.stderr.write("ERROR: translation template not available '{}'".format(file_template))
    exit(errno.ENOENT)

  locales = {}
  for ROOT, DIRS, FILES in os.walk(dir_locale):
    for f in FILES:
      if f != "debreate.po":
        continue
      f = paths.join(ROOT, f)
      _id = os.path.basename(os.path.dirname(f))
      locales[_id] = f

  params = [
    # style
    "--indent", "--sort-output", "--no-location", "--no-wrap",
    # suppress progress bars
    "--silent",
    # write to stdout
    "--output-file=-"
  ]

  for _id in locales:
    file_po = locales[_id]
    res = subprocess.run([cmd_msgmerge, "--lang={}".format(_id)] + params
        + [file_po, file_template], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if res.returncode != 0:
      sys.stderr.write("subprocess returned error:\n\n{}\n".format(res.stdout.decode("utf-8")))
      exit(res.returncode)

    m_strings = res.stdout.decode("utf-8")
    content_orig = ""
    if os.path.isfile(file_po):
      content_orig = fileio.readFile(file_po)

    if m_strings != content_orig:
      fileio.writeFile(file_po, m_strings)
      print("updated translation '{}' ({})".format(_id, file_po))
    else:
      print("translation unchanged '{}' ({})".format(_id, file_po))


if __name__ == "__main__":
  parseStrings()
  updateTranslations()
