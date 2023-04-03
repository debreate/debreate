
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import os
import sys

from libdbr import paths


def init():
  checkPathSeparator()
  checkSystemRoot()

def checkPathSeparator():
  if sys.platform == "win32":
    assert os.sep == "\\"
  else:
    assert os.sep == "/"

def checkSystemRoot():
  sys_root = paths.getSystemRoot()
  if sys.platform == "win32":
    assert sys_root == os.getenv("SystemDrive") + "\\"
  else:
    assert sys_root == "/"
