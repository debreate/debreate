
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************


version_major = 0
version_minor = 1
version_dev = 9
version_tuple = (version_major, version_minor)

## Retrieves version information as a string.
def version():
  ver = "{}.{}".format(version_major, version_minor)
  if version_dev >0:
    ver += "-dev{}".format(version_dev)
  return ver
