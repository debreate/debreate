
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import codecs
import errno
import os
import re
import shutil

from zipfile import ZipFile


# line ending delimeter
__le = "\n"

# default file & directory permissions
__perm = {"f": 0o664, "e": 0o775, "d": 0o775}

## Sets line ending delimeter
#
#  @param delim
#    Value to use for file line endings.
def setLineEndings(delim):
  global __le
  __le = delim

## Makes all line endings uniform.
#
#  @param data
#    String to be cleaned.
#  @return
#    Formatted string.
def _cleanLineEndings(data):
  global __le

  data = data.replace("\r\n", "\n").replace("\r", "\n")
  if __le != "\n":
    data = data.replace("\n", __le)
  return data

## Reads data from a text file.
#
#  @param filepath
#    Path to file to be read.
#  @return
#    Text contents of file.
def readFile(filepath):
  fin = codecs.open(filepath, "r", "utf-8")
  data = fin.read()
  fin.close()
  return _cleanLineEndings(data)

## Writes text or binary data to a file without preserving previous contents.
#
#  @param filepath
#    Path fo file to be written.
#  @param data
#    String or list of strings to export.
#  @param binary
#    Open file in binary mode.
#  @param mode
#    File permissions.
#  @param verbose
#    If true, print extra information.
def writeFile(filepath, data, binary=False, mode=__perm["f"], verbose=False):
  if type(data) in (list, tuple):
    data = "\n".join(data)
  # make sure parent directory exists
  dir_parent = os.path.dirname(filepath)
  if dir_parent and not os.path.exists(dir_parent):
    err, msg = makeDir(dir_parent, verbose=verbose)
    if err != 0:
      __logger.error(msg)
      raise Exception(msg)
      return
  if binary:
    fout = codecs.open(filepath, "wb")
    fout.write(data)
  else:
    fout = codecs.open(filepath, "w", "utf-8")
    fout.write(_cleanLineEndings(data))
  fout.close()
  os.chmod(filepath, mode)
  if verbose:
    print("create file '{}' (mode={})".format(filepath, oct(mode)[2:]))

## Writes text data to a file while preserving previous contents.
#
#  @param filepath
#    Path to file to be written.
#  @param data
#    String or list of strings to export.
#  @param mode
#    File permissions.
#  @param verbose
#    If true, print extra information.
def appendFile(filepath, data, mode=__perm["f"], verbose=False):
  fin_data = []
  # don't try to append to file that doesn't exist
  if os.path.isfile(filepath):
    fin_data.append(readFile(filepath))
  if type(data) in (list, tuple):
    fin_data += list(data)
  else:
    fin_data.append(data)
  writeFile(filepath, fin_data, False, mode, verbose)


__timestamps = {}

## Checks a files timestamp information.
#
#  @param filepath
#    Path to file to be checked.
#  @return
#    Timestamp string & flag denoting change from a previous timestamp.
def checkTimestamp(filepath):
  changed = False
  ts = os.stat(filepath).st_mtime
  if filepath in __timestamps:
    changed = ts != __timestamps[filepath]
  __timestamps[filepath] = ts
  return ts, changed

## Checks if a target file or directory exists
#
#  @param target
#    Path to check.
#  @param action
#    Action being taken (for debugging).
#  @param add_parent
#    If true, creates parent directory tree.
#  @return
#    Error code & message.
def __checkNotExists(target, action=None, add_parent=False):
  err = errno.EEXIST
  msg = ""
  if action:
    msg += "cannot " + action + ", "

  if os.path.exists(target):
    if os.path.isdir(target):
      err = errno.EISDIR
      msg += "directory"
    else:
      msg += "file"
    msg += " exists: {}".format(target)
    return err, msg

  if add_parent:
    dir_parent = os.path.dirname(target)
    if not os.path.exists(dir_parent):
      os.makedirs(dir_parent)
    elif not os.path.isdir(dir_parent):
      return err, "cannot create directory, file exists: {}".format(dir_parent)
  return 0, None

## Checks that a target path is not a directory.
#
#  @param target
#    Target path to be checked.
#  @param action
#    Action being taken (for debugging).
#  @return
#    Error code & message.
def __checkNotDir(target, action=None):
  msg = ""
  if action:
    msg += "cannot " + action + ", "
  if os.path.exists(target) and os.path.isdir(target):
    return errno.EISDIR, msg + "directory exists: {}".format(target)
  return 0, None

## Checks if a file exists on the filesystem.
#
#  @param filepath
#    Path to file to be checked.
#  @param action
#    Action being taken (for debugging).
#  @return
#    Error code & message.
def __checkFileExists(filepath, action=None):
  msg = ""
  if action:
    msg += "cannot " + action + " file, "

  if not os.path.exists(filepath):
    msg += "does not exist: {}".format(filepath)
    return errno.ENOENT, msg
  if os.path.isdir(filepath):
    msg += "is a directory: {}".format(filepath)
    return errno.EISDIR, msg
  return 0, None

## Checks if a directory exists on the filesystem.
#
#  @param source
#    Path to directory to be checked.
#  @param action
#    Action being taken (for debugging).
#  @return
#    Error code & message.
def __checkDirExists(source, action=None):
  msg = ""
  if action:
    msg += "cannot " + action + " directory, "

  if not os.path.exists(source):
    msg += "source does not exist: {}".format(source)
    return errno.ENOENT, msg
  if not os.path.isdir(source):
    msg += "source is a file: {}".format(source)
    return errno.EEXIST, msg
  return 0, None

## Creates a new directory if one does not already exist.
#
#  @param dirpath
#    Path to new directory.
#  @param
#    Directory permissions.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def makeDir(dirpath, mode=__perm["d"], verbose=False):
  err, msg = __checkNotExists(dirpath, "create directory")
  if err != 0:
    return err, msg
  os.makedirs(dirpath)
  if not os.path.isdir(dirpath):
    return 1, "failed to create directory, an unknown error occured: {}".format(dirpath)
  os.chmod(dirpath, mode)
  if verbose:
    print("new directory '{}' (mode={})".format(dirpath, oct(mode)[2:]))
  return 0, None

## Deletes a file from the filesystem.
#
#  @param filepath
#    Path to file to be removed.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def deleteFile(filepath, verbose=False):
  if os.path.exists(filepath):
    if os.path.isdir(filepath):
      return errno.EISDIR, "cannot delete file, directory exists: {}".format(filepath)
    os.remove(filepath)
    if os.path.exists(filepath):
      return 1, "failed to delete file, an unknown error occured: {}".format(filepath)
    if verbose:
      print("delete file '{}'".format(filepath))
  return 0, None

## Delete a directory tree from the filesystem.
#
#  @param dirpath
#    Path to directory to be removed.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def deleteDir(dirpath, verbose=False):
  if os.path.exists(dirpath):
    if not os.path.isdir(dirpath):
      return errno.EEXIST, "cannot delete directory, file exists: {}".format(dirpath)
    for obj in os.listdir(dirpath):
      objpath = os.path.join(dirpath, obj)
      if not os.path.isdir(objpath):
        err, msg = deleteFile(objpath, verbose)
      else:
        err, msg = deleteDir(objpath, verbose)
      if err != 0:
        return err, msg
    if len(os.listdir(dirpath)) != 0:
      return errno.ENOTEMPTY, "failed to delete directory, not empty: {}".format(dirpath)
    os.rmdir(dirpath)
    if os.path.exists(dirpath):
      return 1, "failed to delete directory, an unknown error occurred: {}".format(dirpath)
    if verbose:
      print("delete directory '{}'".format(dirpath))
  return 0, None

## Copies a file on the filesystem.
#
#  @param source
#    Path to file to be copied.
#  @param target
#    Path to copy target.
#  @param name
#    Optional filename to use (assumes `target` is a directory).
#  @param mode
#    File permissions.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def copyFile(source, target, name=None, mode=__perm["f"], verbose=False):
  if name:
    target = os.path.join(target, name)
  err, msg = __checkFileExists(source, "copy")
  if err != 0:
    return err, msg
  err, msg = __checkNotExists(target, "copy file", True)
  if err != 0:
    return err, msg
  shutil.copyfile(source, target)
  if not os.path.exists(target):
    return 1, "failed to copy file, an unknown error occurred: {}".format(target)
  os.chmod(target, mode)
  if verbose:
    print("copy '{}' -> '{}' (mode={})".format(source, target, oct(mode)[2:]))
  return 0, None

## Copies a file on the filesystem & marks as executable.
#
#  @param source
#    Path to file to be copied.
#  @param target
#    Path to copy target.
#  @param name
#    Optional filename to use (assumes `target` is parent directory).
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def copyExecutable(source, target, name=None, verbose=False):
  return copyFile(source, target, name, __perm["e"], verbose)

## Copies a directory on the filesystem.
#
#  @param source
#    Path to directory to be copied.
#  @param target
#    Path to copy target.
#  @param name
#    Optional directory name to use (assumes `target` is parent directory).
#  @param _filter
#    Optional file filter.
#  @param exclude
#    Optional excludes filter.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def copyDir(source, target, name=None, mode=__perm["d"], _filter="", exclude=None, verbose=False):
  if name:
    target = os.path.join(target, name)
  else:
    name = os.path.basename(target)
  if exclude and re.search(exclude, name):
    if verbose:
      print("excluding directory from copy: '{}'".format(name))
    return 0, None
  err, msg = __checkDirExists(source, "copy")
  if err != 0:
    return err, msg
  # ~ err, msg = __checkNotExists(target, "copy directory")
  # ~ if err != 0:
    # ~ return err, msg
  contents = os.listdir(source)
  if len(contents) == 0:
    if verbose:
      print("directory empty, not copying: '{}'".format(source))
    return 0, None
  if not os.path.isdir(target):
    err, msg = makeDir(target, False)
    if err != 0:
      return err, msg
    os.chmod(target, mode)
  if not os.path.isdir(target):
    return 1, "failed to copy directory, an unknown error occurred: {}".format(target)
  if verbose:
    print("copy '{}' -> '{}' (mode={})".format(source, target, oct(mode)[2:]))
  for obj in contents:
    if exclude and re.search(exclude, obj):
      if verbose:
        print("excluding pattern from copy: '{}'".format(obj))
      continue
    objsource = os.path.join(source, obj)
    objtarget = os.path.join(target, obj)
    if not os.path.isdir(objsource):
      if re.search(_filter, obj):
        err, msg = copyFile(objsource, objtarget, None, mode-0o111, verbose)
    else:
      err, msg = copyDir(objsource, objtarget, None, mode, _filter, exclude, verbose)
    if err != 0:
      return err, msg
  return 0, None

## Moves a file on the filesystem.
#
#  @param source
#    Path to file to be moved.
#  @param target
#    Path to copy target.
#  @param name
#    Optional filename to use (assumes `target` is a directory).
#  @param mode
#    File permissions.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def moveFile(source, target, name=None, mode=__perm["f"], verbose=False):
  if name:
    target = os.path.join(target, name)
  err, msg = __checkFileExists(source, "move")
  if err != 0:
    return err, msg
  err, msg = __checkNotExists(target, "move file", True)
  if err != 0:
    return err, msg
  shutil.move(source, target)
  if os.path.exists(source) or not os.path.exists(target):
    return 1, "failed to move file, an unknown error occurred: {}".format(target)
  os.chmod(target, mode)
  if verbose:
    print("move '{}' -> '{}' (mode={})".format(source, target, oct(mode)[2:]))
  return 0, None

## Moves a directory on the filesystem.
#
#  @param source
#    Path to directory to be moved.
#  @param target
#    Path to copy target.
#  @param name
#    Optional directory name to use (assumes `target` is parent directory).
#  @param mode
#    Directory permissions.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def moveDir(source, target, name=None, mode=__perm["d"], verbose=False):
  if name:
    target = os.path.join(target, name)
  err, msg = __checkDirExists(source, "move")
  if err != 0:
    return err, msg
  # ~ err, msg = __checkNotExists(target, "move directory")
  # ~ if err != 0:
    # ~ return err, msg
  contents = os.listdir(source)
  if len(contents) == 0:
    if verbose:
      print("directory empty, not moving: '{}'".format(source))
    return 0, None
  if not os.path.isdir(target):
    err, msg = makeDir(target, False)
    if err != 0:
      return err, msg
    os.chmod(target, mode)
  if not os.path.isdir(target):
    return 1, "failed to move directory, an unknown error occurred: {}".format(target)
  for obj in contents:
    objsource = os.path.join(source, obj)
    objtarget = os.path.join(target, obj)
    if not os.path.isdir(objsource):
      err, msg = moveFile(objsource, objtarget, None, mode-0o111, verbose)
    else:
      err, msg = moveDir(objsource, objtarget, None, mode, verbose)
    if err != 0:
      return err, msg
  err, msg = deleteDir(source, False)
  if err != 0:
    return err, msg
  if verbose:
    print("move '{}' -> '{}' (mode={})".format(source, target, oct(mode)[2:]))
  return 0, None

## Compresses a file into a zip archive.
#
#  TODO:
#  - support more archive formats
#  - set permissions of archived files
#
#  @param sourcefile
#    Path to file to be added.
#  @param archive
#    Path to archive or open archive stream.
#  @param amend
#    Add to without deleting old contents.
#  @param mode
#    File permissions.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def packFile(sourcefile, archive, amend=False, mode=__perm["f"], verbose=False):
  err, msg = __checkFileExists(sourcefile)
  if err != 0:
    return err, msg
  new_archive = type(archive) != ZipFile
  zopen = archive
  if new_archive:
    err, msg = __checkNotDir(archive, "create zip")
    if err != 0:
      return err, msg
    # create a new archive file
    zopen = ZipFile(archive, "a" if amend else "w")
  zopen.write(sourcefile)
  if verbose:
    print("compress '{}' => '{}'".format(sourcefile, archive))
  # if ZipFile was passed, calling instruction should close the file
  if new_archive:
    zopen.close()
    os.chmod(archive, mode)
    if verbose:
      print("added one file to archive '{}' (mode={})".format(archive, oct(mode)[2:]))
  return 0, None

## Compresses a directory into a zip archive.
#
#  TODO:
#  - support more archive formats
#  - set permissions of archived files
#
#  @param sourcedir
#    Path to directory to be added.
#  @param archive
#    Path to archive.
#  @param incroot
#    If true, include parent directory tree.
#  @param amend
#    Add to without deleting old contents.
#  @param mode
#    File permissions.
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def packDir(sourcedir, archive, incroot=False, amend=False, mode=__perm["f"], verbose=False):
  err, msg = __checkDirExists(sourcedir)
  if err != 0:
    return err, msg
  err, msg = __checkNotDir(archive, "create zip")
  if err != 0:
    return err, msg

  dir_start = os.getcwd()

  # normalize path to archive
  a_basename = os.path.basename(archive)
  a_dirname = os.path.dirname(archive)
  if a_dirname:
    os.chdir(a_dirname)
  a_dirname = os.getcwd()
  archive = os.path.join(a_dirname, a_basename)
  os.chdir(dir_start)

  # clean up path name
  os.chdir(sourcedir)
  dir_abs = os.getcwd()
  idx_trim = len(dir_abs) + 1
  if incroot:
    os.chdir(dir_start)
    idx_trim = len(dir_start) + 1

  zopen = ZipFile(archive, "a" if amend else "w")
  z_count_start = len(zopen.namelist())
  for ROOT, DIRS, FILES in os.walk(dir_abs):
    for f in FILES:
      f = os.path.join(ROOT, f)[idx_trim:]
      err, msg = packFile(f, zopen, True, verbose)
      if err != 0:
        # make sure to close stream in case of error
        zopen.close()
        return err, msg
  z_count_end = len(zopen.namelist())
  zopen.close()
  os.chmod(archive, mode)

  os.chdir(dir_start)
  if z_count_end == 0:
    print("WARNING: no files compressed, deleting empty archive '{}'".format(archive))
    err, msg = deleteFile(archive, verbose)
    if err != 0:
      return err, msg
  elif verbose:
    z_count_diff = z_count_end - z_count_start
    if z_count_diff == 0:
      print("archive unchanged '{}'".format(archive))
    else:
      print("added {} file(s) to archive '{}' (mode={})".format(z_count_diff, archive, oct(mode)[2:]))
  return 0, None

## Extracts contents of a zip archive.
#
#  TODO: support more archive formats
#
#  @param filepath
#    Path to archive.
#  @param dir_target
#    Directory where contents should be extracted (default: parent directory of archive).
#  @param verbose
#    If true, print extra information.
#  @return
#    Error code & message.
def unpackArchive(filepath, dir_target=None, verbose=False):
  if not os.path.isfile(filepath):
    return errno.ENOENT, "cannot extract zip, file not found: {}".format(filepath)

  dir_start = os.getcwd()
  dir_parent = os.path.dirname(filepath)
  if dir_target == None:
    dir_target = os.path.join(dir_parent, os.path.basename(filepath).lower().split(".zip")[0])

  if os.path.exists(dir_target):
    if not os.path.isdir(dir_target):
      return errno.EEXIST, "cannot extract zip, file exists: {}".format(dir_target)
    shutil.rmtree(dir_target)
  os.makedirs(dir_target)

  os.chdir(dir_target)
  if verbose:
    print("extracting contents of {} ...".format(filepath))
  zopen = ZipFile(filepath, "r")
  zopen.extractall()
  zopen.close()
  # return to original directory
  os.chdir(dir_start)
  return 0, None
