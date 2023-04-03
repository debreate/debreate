
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

import os

from libdbr import paths


## Checks if app is running portably.
#
#  @return
#    True if not installed.
def isPortable():
  return os.path.isfile(paths.join(paths.getAppDir(), "INSTALLED"))
