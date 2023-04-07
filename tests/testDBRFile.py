#!/usr/bin/env python3

import os
import sys

sys.path.insert(0, "lib")

from libdebreate         import appinfo
from libdebreate.dbrfile import DBRFile
from libdbr              import paths


def init():
  # legacy project
  filepath = paths.join(paths.getAppDir(), "tests/data/legacy_project_sample.dbp")
  assert os.path.isfile(filepath)

  project = DBRFile(filepath)
  assert project.getFile() == filepath
  project = DBRFile()
  assert project.getFile() == None
  project.setFile(filepath)
  assert project.getFile() == filepath
  assert project.getAppVersion() == (0, 7)
  assert project.getDBRStandard() == (0, 9)
