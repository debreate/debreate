## \package f_export.permiss

# MIT licensing
# See: docs/LICENSE.txt


import os

from libdbr.logger import Logger


__logger = Logger(__name__)

## Sets files executable bit
#
#  FIXME: Check timestamp
#
#  \param target
#  Absolute path to file
#  \param executable
#  Sets or removes executable bit
def SetFileExecutable(target, executable=True):
  __logger.deprecated(__name__, SetFileExecutable.__name__, "os.chmod")

  if os.path.isfile(target):
    if executable:
      mode = 0o775

    else:
      mode = 0o664

    os.chmod(target, mode)

    if os.access(target, mode):
      return True

  return False
