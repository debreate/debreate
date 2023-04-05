
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import bz2
import gzip
import lzma
import os
import zlib

from libdbr import fileio
from libdbr import paths


def init():
  dir_sandbox = paths.join(paths.getAppDir(), "tests/sandbox")
  assert os.path.isdir(dir_sandbox)

  file_dummy1 = paths.join(dir_sandbox, "dummy1.txt")
  file_dummy2 = paths.join(dir_sandbox, "dummy2.txt")
  file_dummy3 = paths.join(dir_sandbox, "dummy3.txt")
  assert os.path.isfile(file_dummy1)
  assert os.path.isfile(file_dummy2)
  assert not os.path.exists(file_dummy3)

  # error test unsupported format
  err, msg = fileio.compressFile(file_dummy1, file_dummy3 + ".foobar", form="foobar")
  assert err != 0
  assert not os.path.isfile(file_dummy3 + ".foobar")

  # error test source doesn't exist
  err, msg = fileio.compressFile(file_dummy3, file_dummy3 + ".gz")
  assert err != 0
  assert not os.path.isfile(file_dummy3 + ".gz")

  # error test target is file
  err, msg = fileio.compressFile(file_dummy1, file_dummy2)
  assert err != 0

  # error test target is directory
  err, msg = fileio.compressFile(file_dummy1, dir_sandbox)
  assert err != 0

  c_formats = fileio.getCompressionFormats()
  for form in c_formats:
    if form == "zlib":
      decompressor = gzip.open
      f_ext = ".gz"
    else:
      if form == "zip":
        decompressor = c_formats[form]
      else:
        decompressor = c_formats[form].open
      f_ext = "." + form
    filepath = paths.join(dir_sandbox, "compressed_file" + f_ext)
    assert not os.path.exists(filepath)
    err, msg = fileio.compressFile(file_dummy1, filepath, form=form)
    if err != 0:
      raise Exception("error code {}: {}".format(err, msg))
    assert os.path.isfile(filepath)
    try:
      fin = decompressor(filepath)
      fin.close()
    except Exception as e:
      print(e)
      assert False
    err, msg = fileio.deleteFile(filepath)
    if err != 0:
      raise Exception("error code {}: {}".format(err, msg))
    assert not os.path.isfile(filepath)
