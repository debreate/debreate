
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Redefines & adds some new codes to the system errno module.
#
#  @module globals.errno

import copy
import errno
import types
import wx


# mypy: disable-error-code="attr-defined"

# @todo Convert these to dbrerror
ERR_DIR_NOT_AVAILABLE = wx.NewId()
ERR_FILE_READ = wx.NewId()
ERR_FILE_WRITE = wx.NewId()

error_definitions = {
  ERR_DIR_NOT_AVAILABLE: "Directory Not Available",
  ERR_FILE_READ: "Could Not Read File",
  ERR_FILE_WRITE: "Could Not Write File",
}

dbrerrno = types.new_class("dbrerrno")
for attr in errno.__dict__:
  setattr(dbrerrno, attr, copy.deepcopy(errno.__dict__[attr]))

current_code = sorted(dbrerrno.errorcode.keys())[-1]
def addCode(_id):
  global current_code
  current_code += 1
  setattr(dbrerrno, _id, current_code)

setattr(dbrerrno, "addCode", addCode)
# REMOVEME:
setattr(dbrerrno, "SUCCESS", 0)

dbrerrno.addCode("EBADFT")
dbrerrno.addCode("ECNCLD")
dbrerrno.addCode("FEMPTY")
dbrerrno.addCode("EUNKNOWN")
dbrerrno.addCode("FCONFLICT")
