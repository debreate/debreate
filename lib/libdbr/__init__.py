
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

from . import strings


__version = (0, 1)
__version_dev = 10

## Retrieves version information.
def version():
  return __version

## Retreives version information as a string.
def versionString():
  ver = strings.toString(__version, sep=".")
  if __version_dev > 0:
    ver += "-dev{}".format(__version_dev)
  return ver
