
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.imagelist

import wx

from dbr.image     import GetBitmap
from libdbr.logger import Logger


logger = Logger(__name__)

## List of images used by `ui.tree.DirectoryTree`.
#
#  @todo
#    FIXME: Custom images should be generated dynamically using bitmaps found in MIME directory.
class DirectoryImageList(wx.ImageList):
  def __init__(self, width, height, mask=True, initial_count=1):
    wx.ImageList.__init__(self, width, height, mask, initial_count)

    directory_images = []

    custom_images = (
      "audio-generic",
      "computer",
      "drive-fixed",
      "drive-floppy",
      "drive-removable",
      "executable-binary",
      "executable-script",
      "failsafe",
      "folder",
      "folder-home",
      "folder-home-open",
      "folder-open",
      "file",
      "image-generic",
      "symlink",
      "video-generic",
      )

    for I in custom_images:
      directory_images.append((GetBitmap(I), I))

    stock_images = (
      (wx.ART_CDROM, "cdrom"),
      (wx.ART_EXECUTABLE_FILE, "executable-binary"),
      (wx.ART_FLOPPY, "drive-floppy"),
      (wx.ART_FOLDER, "folder"),
      (wx.ART_FOLDER_OPEN, "folder-open"),
      (wx.ART_HARDDISK, "drive-fixed"),
      (wx.ART_MISSING_IMAGE, "failsafe"),
      (wx.ART_NORMAL_FILE, "file"),
      (wx.ART_REMOVABLE, "drive-removable"),
      )

    # Use available stock images if a custom image has not been defined
    for SI in stock_images:
      add_stock = True
      for DI in directory_images:
        if SI[1] == DI[1]:
          add_stock = False
          break

      if add_stock:
        directory_images.append(SI)

    aliases = (
      ("audio-generic", ("audio", "audio-file", "file-audio",)),
      ("executable-binary", ("executable", "executable-file", "file-executable",)),
      ("executable-script", ("executable-text", "text-executable",)),
      ("file", ("normal file",)),
      ("drive-floppy", ("floppy", "floppy-drive",)),
      ("drive-fixed", ("hard-disk", "harddisk", "hard-drive", "fixed-drive", "drive",)),
      ("drive-removable", ("removable", "removable-drive",)),
      ("image-generic", ("image", "image-file", "file-image",)),
      ("symlink", ("symbolic-link", "shortcut",)),
      ("video-generic", ("video", "video-file", "file-video",)),
      )

    self.Images = {}

    for I in range(len(directory_images)):
      # Keys are set by index value
      self.Images[directory_images[I][1]] = I

    for ORIG, ALIST in aliases:
      for ALIAS in ALIST:
        self.Images[ALIAS] = self.Images[ORIG]

    for IMAGE in directory_images:
      IMAGE = IMAGE[0]

      if isinstance(IMAGE, wx.Bitmap):
        logger.debug("Adding wx.Bitmap to image list")

        self.Add(IMAGE)

      else:
        logger.debug("Adding bitmap from wx.ArtProvider")

        self.Add(wx.ArtProvider.GetBitmap(IMAGE, wx.ART_CMN_DIALOG, wx.Size(width, height)))


  ## Retrieves image index for setting in `ui.tree.DirectoryTree`.
  #
  #  @param description [\a str]
  #    Name/Description for image.
  #  @return [\a int]
  #    Index of image or index of failsafe image if description doesn't exist.
  def GetImageIndex(self, description):
    if description in self.Images:
      return self.Images[description]

    return self.Images["failsafe"]


## Image list used for ui.tree.DirectoryTree
sm_DirectoryImageList = DirectoryImageList(16, 16)
