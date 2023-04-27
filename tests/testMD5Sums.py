
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os

import libdbr.bin

from libdbr          import fileio
from libdbr          import paths
from libdbr.logger   import Logger
from libdbr.misc     import generateMD5Hash
from libdbr.unittest import assertEquals
from libdbr.unittest import assertTrue


_logger = Logger(__name__)

def init():
  cmd_md5 = paths.getExecutable("md5sum")
  _logger.debug("md5sum command: {}".format(cmd_md5))

  if not cmd_md5:
    _logger.warn("md5sum command not available, skipping tests")
    return 0

  file_init = paths.join(paths.getAppDir(), "init.py")
  assertTrue(os.path.isfile(file_init))

  err, res1 = libdbr.bin.execute(cmd_md5, file_init)
  res1 = res1[0:res1.index(" ")]
  # Windows version of md5sum command prepends node separator
  res1 = res1.strip(os.sep)
  _logger.debug("result 1: {}".format(res1))
  res2 = generateMD5Hash(fileio.readFile(file_init, binary=True))
  _logger.debug("result 2: {}".format(res2))

  assertEquals(res1, res2)

  # TODO: create test package to check generated hashes
