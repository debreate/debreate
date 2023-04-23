
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.fileitem

import os

from dbr.colors      import COLOR_dir
from dbr.colors      import COLOR_executable
from dbr.colors      import COLOR_link
from globals.strings import IsString
from libdbr          import fileinfo
from libdbr          import fileio
from libdbr          import strings


## @todo Doxygen
class FileType:
  NORM = None
  EXEC = COLOR_executable
  LINK = COLOR_link
  DIR = COLOR_dir


## An object that represents a file.
#
#  @todo
#    FIXME: need method to get relative path
class FileItem:
  def __init__(self, path, target=None, ignore_timestamp=False):
    self.Path = path
    self.Target = target

    # Timestamp is set at construction
    self.Timestamp = None
    if not ignore_timestamp:
      self.Timestamp = fileinfo.checkTimestamp(self.Path)

    # Defaults to normal file
    self.Type = FileType.NORM
    self.SetType()

  ## Checks if the file exists on the filesystem.
  def Exists(self):
    return os.path.isfile(self.Path)

  ## Retrieves file's basename.
  def GetBasename(self):
    return os.path.basename(self.Path)

  ## Retrieves file's full path.
  def GetPath(self):
    return self.Path

  ## Retrieves file's target directory
  def GetTarget(self):
    return self.Target

  ## Retrieves the file's timestamp from memory.
  #
  #  NOTE: May differ from actual timestamp.
  #  Call 'TimestampChanged' to update.
  #
  #  @todo return
  def GetTimestamp(self):
    return self.Timestamp

  ## Retrieves the file type (normal file, directory, symbolic link, or executable).
  #
  #  @todo return
  def GetType(self):
    return self.Type

  ## Checks if the file has a target installation directory.
  #
  #  @todo return
  def HasTarget(self):
    return IsString(self.Target) and not strings.isEmpty(self.Target)

  ## Checks if the item represented is a directory.
  #
  #  @todo return
  def IsDirectory(self):
    return os.path.isdir(self.Path)

  ## Checks if the item represented is a regular file
  def IsFile(self):
    return os.path.isfile(self.Path)


  ## Checks if file is executable.
  #
  #  @todo return
  def IsExecutable(self):
    if self.IsFile():
      return os.access(self.Path, os.X_OK)
    return False

  ## Reads file's contents into memory.
  #
  #  @param split
  #    If \b \e True, splits the text into a list.
  #  @param convert
  #    Type of list to split contents into (can be \b \e tuple or \b \e list).
  #    FIXME: Use boolean???
  #  @param noStrip
  #    \b \e String of leading & trailing characters to not strip.
  #  @todo return
  def Read(self, split=False, convert=tuple, noStrip=None):
    return convert(fileio.readFile(self.Path).split("\n"))

  ## Sets file's path & basename.
  #
  #  @todo parameters
  def SetPath(self, path):
    self.Path = path

  ## Sets file's target directory.
  #
  #  @todo parameters
  def SetTarget(self, target):
    self.Target = target

  ## Sets file type.
  def SetType(self):
    if os.path.isdir(self.Path):
      self.Type = FileType.DIR
    elif os.path.islink(self.Path):
      self.Type = FileType.LINK
    elif os.access(self.Path, os.X_OK):
      self.Type = FileType.EXEC

  ## Checks if timestamp has been modified & updates.
  #
  #  @todo return
  def TimestampChanged(self):
    # Set file's timestamp if not already done
    if not self.Timestamp:
      self.Timestamp = fileinfo.checkTimestamp(self.Path)
      return False

    current_stamp = fileinfo.checkTimestamp(self.Path)
    if current_stamp != self.Timestamp:
      self.Timestamp = current_stamp
      return True
    return False
