
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.containers

import wx


## Tests if a container contains any of a list of items.
def Contains(cont, items):
  if not isinstance(items, (tuple, list, dict)):
    return items in cont
  for ITEM in items:
    if ITEM in cont:
      return True
  return False


## Retrieves the number of items contained within the object.
#
#  Compatibility function for older wx versions.
def GetItemCount(cont):
  if wx.MAJOR_VERSION <= 2:
    return len(cont.GetChildren())
  return cont.GetItemCount()
