
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

# miscellaneous functions

import hashlib

from libdbr import fileio


## Creates a hash from string or bytes data.
#
#  @param data
#    String or bytes data to process.
#  @return
#    MD5 hex hash string.
def generateMD5Hash(data):
  if type(data) == str:
    data = data.encode()
  tmp = hashlib.md5()
  tmp.update(data)
  return tmp.hexdigest()

## Parses most recent changes from a changelog-style file.
#
#  @param changelog
#    Path to changelog file.
#  @return
#    String containing topmost section of changelog data.
def getLatestChanges(changelog):
  data = fileio.readFile(changelog)
  if not data:
    return ""
  changes = []
  in_changes = False
  for li in data.split("\n"):
    if li.strip():
      in_changes = True
      changes.append(li)
    elif in_changes:
      break
  if changes:
    # remove first line if it is a section header
    header = changes[0].strip()
    if not header.startswith("-") and not header.startswith("*"):
      changes.pop(0)
    return "\n".join(changes)
  return ""
