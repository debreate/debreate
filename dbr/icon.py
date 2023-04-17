
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.icon

import wx


## @todo
#    Doxygen.
class Icon(wx.Icon):
  def __init__(self, name, desiredWidth=-1, desiredHeight=-1):
    bm_type = self.GetBitmapType(name)
    wx.Icon.__init__(self, name, bm_type, desiredWidth, desiredHeight)

  ## @todo
  #    Doxygen.
  def GetBitmapType(self, filename):
    if filename:
      bm_types = {
        "png": wx.BITMAP_TYPE_PNG,
        }
      suffix = filename.split(".")[-1]
      if suffix in bm_types:
        return bm_types[suffix]
    return wx.BITMAP_TYPE_ANY
