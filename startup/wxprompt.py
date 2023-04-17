
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## @module startup.wxprompt

import errno
import os
import subprocess
import sys

if __name__ == "__main__":
  # include libdbr in module search path
  sys.path.insert(0, os.path.join(os.path.dirname(sys.argv[0]), "../", "lib"))

from libdbr         import paths
from libdbr         import sysinfo
from libdbr.logger  import Logger
from libdbr.modules import installModule


__logger = Logger(__name__)

## @todo Doxygen
def promptForWxInstall():
  print("Debreate requires wxPython, do you want me to try to download and install it?")
  if input("yes/no (this could take a while): ").lower().strip() not in ("y", "yes"):
    __logger.error("wxPython not found, cannot continue")
    return errno.ENOENT
  installModule("wheel")
  installModule("setuptools")
  installModule("wx", "wxpython==4.1.1")
  return 0

if __name__ == "__main__":
  exit(promptForWxInstall())
