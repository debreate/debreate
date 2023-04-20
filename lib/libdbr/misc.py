
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Miscellaneous functions.
#
#  @module libdbr.misc

import hashlib
import re

from .       import dateinfo
from .       import fileio
from .logger import Logger


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

## Formats list of changes to Debian style changelog.
#
#  @param changes
#    String to be converted.
#  @param info
#    Dictionary containing parameters to be added.
#  @return
#    Debian compliant changelog entry.
def formatDebianChanges(changes, info, indent=0, tabs=False):
  if type(changes) == str:
    changes = changes.split("\n")
  if indent < 1:
    # default indent
    indent = 1 if tabs else 2
  _i = "".rjust(indent, "\t" if tabs else " ")
  ws_count = len(_i) # number of whitespace used in indent
  if tabs:
    ws_count *= 2
  try:
    dchanges = ["{} ({}) {}; urgency={}"
        .format(info["package"], info["version"], info["dist"], info["urgency"]), ""]
    for li in changes:
      if re.match(r"^(-|\*) ", li, flags=re.M):
        dchanges.append(re.sub(r"^(-|\*) ", "  * ", li, flags=re.M))
      elif re.match(r"^{}(-|\*) ".format(_i), li, flags=re.M):
        dchanges.append(re.sub(r"^{}(-|\*) ".format(_i), "".rjust(ws_count*2, " "), li, flags=re.M))
      else:
        if _i:
          # use standard indentation
          ic = 0
          while li.startswith(_i):
            ic += 1
            # ~ li = re.sub(r"^{}".format(_i), "", li, count=1, flags=re.M)
            li = li.removeprefix(_i)
          for ix in range(ic):
            li = "  " + li
        dchanges.append("  " + li)
    dchanges.append("")
    dchanges.append(" -- {} <{}>  {}"
        .format(info["author"], info["email"], dateinfo.getDebianizedDate()))

    for idx in reversed(range(len(dchanges))):
      li = dchanges[idx]
      ll = len(li)
      # lintian throws a warning for lines longer than 80 characters
      if ll > 80:
        indent_idx = 0
        for char in li:
          if char not in (" ", "*"):
            break
          indent_idx += 1

        break_point = 80
        for c_idx in reversed(range(break_point)):
          if li[c_idx] in (" ", "\t"):
            break_point = c_idx
            break

        li_head = li[0:break_point]
        li_tail = li[break_point+1:]
        li_tail = li_tail.rjust(len(li_tail) + indent_idx + 2)

        dchanges.insert(idx+1, li_tail)
        dchanges[idx] = li_head

    res = "\n".join(dchanges)
    # ensure trailing newline
    if not res.endswith("\n"):
      res += "\n"
    return res
  except KeyError as e:
    Logger(__name__ + "." + formatDebianChanges.__name__) \
        .error("missing required info key {}".format(e))
  return ""
