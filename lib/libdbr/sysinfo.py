
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os
import sys

from libdbr import config


if sys.platform == "win32":
  __os_name = sys.platform
else:
  if os.path.isfile("/etc/lsb-release"):
    __os_name = config.getValue("DISTRIB_ID", filepath="/etc/lsb-release")
if not __os_name:
  __os_name = "unknown"
__os_name = __os_name.lower()

## Retrieves detected operating system name.
def getOSName():
  return __os_name
