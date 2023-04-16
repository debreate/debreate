
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************


from libdbr import strings


__version = (0, 8)
__version_dev = 5
__dbr_standard = (1, 0)

## Retrieves app version.
#
#  @return
#    App version tuple.
def getVersion():
  return __version

## Retreives app development version.
#
#  @return
#    Development version integer.
def getVersionDev():
  return __version_dev

## Retrieves app version.
#
#  @return
#    App version string.
def getVersionString():
  ver = strings.toString(__version, sep=".")
  if __version_dev > 0:
    ver += "-dev{}".format(__version_dev)
  return ver

## Retrieves config version standard.
#
#  @return
#    Config standard tuple.
def getDBRStandard():
  return __dbr_standard
