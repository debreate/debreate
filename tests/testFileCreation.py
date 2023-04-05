
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os

from libdbr import fileio
from libdbr import paths


def init():
  dir_sandbox = paths.join(paths.getAppDir(), "tests/sandbox")
  assert os.path.isdir(dir_sandbox)

  file_test = paths.join(dir_sandbox, "test_create_file.txt")
  assert not os.path.exists(file_test)
  fileio.createFile(file_test)
  assert os.path.isfile(file_test)
  fileio.deleteFile(file_test)
  assert not os.path.exists(file_test)

  file_test = paths.join(dir_sandbox, "test_create_file.bin")
  assert not os.path.exists(file_test)
  fileio.createFile(file_test, binary=True)
  assert os.path.isfile(file_test)
  fileio.deleteFile(file_test)
  assert not os.path.exists(file_test)
