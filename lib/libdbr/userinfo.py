
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## User information.
#
#  @module libdbr.userinfo

import os
import sys

if sys.platform == "win32":
  import ctypes


## Checks administrative permissions for current user.
#
#  @return
#    True if user has elevate privileges.
def isAdmin():
  if sys.platform == "win32":
    return ctypes.windll.shell32.IsUserAnAdmin() != 0 # @UndefinedVariable
  return os.getuid() == 0 # pylint: disable=no-member
