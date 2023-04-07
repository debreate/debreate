
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************


__version = 0.8
__version_dev = 5
__dbr_standard = 1.0


## Retrieves app version.
#
#  @return
#    App version float.
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
  ver = "{}".format(__version)
  if __version_dev > 0:
    ver += "-dev{}".format(__version_dev)
  return ver

## Retrieves app version.
#
#  @return
#    App version tuple.
def getVersionTuple():
  ver = []
  for v in getVersionString().split("."):
    if "-" in v:
      v = v.split("-")[0]
    ver.append(int(v))
  return tuple(ver)

## Retrieves config version standard.
#
#  @return
#    Config standard float.
def getDBRStandard():
  return __dbr_standard

## Retrieves config version standard.
#
#  @return
#    Config standard tuple.
def getDBRStandardTuple():
  ver = []
  for v in "{}".format(__dbr_standard).split("."):
    ver.append(int(v))
  return tuple(ver)
