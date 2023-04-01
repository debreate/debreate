
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import codecs
import os


# line ending delimiter
_le = "\n"

## Sets line ending delimiter
#
#  @param delim
#    Value to use for file line endings.
def setLineEndings(delim):
  global _le
  _le = delim

## Makes all line endings uniform.
#
#  @param data
#    String to be cleaned.
#  @return
#    Formatted string.
def _cleanLineEndings(data):
  global _le

  data = data.replace("\r\n", "\n").replace("\r", "\n")
  if _le != "\n":
    data = data.replace("\n", _le)
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

## Writes text data to a file without preserving previous contents.
#
#  @param filepath
#    Path to file to be written.
#  @param data
#    String or list of strings to export.
def writeFile(filepath, data):
  if type(data) != str:
    data = "\n".join(data)
  fout = codecs.open(filepath, "w", "utf-8")
  fout.write(_cleanLineEndings(data))
  fout.close()

## Writes text data to a file while preserving previous contents.
#
#  @param filepath
#    Path to file to be written.
#  @param data
#    String or list of strings to export.
def appendFile(filepath, data):
  fin_data = []
  # don't try to append to file that doesn't exist
  if os.path.isfile(filepath):
    fin_data.append(readFile(filepath))
  if type(data) != str:
    fin_data += list(data)
  else:
    fin_data.append(data)
  writeFile(filepath, fin_data)


_timestamps = {}

## Checks a files timestamp information.
#
#  @param filepath
#    Path to file to be checked.
#  @return
#    Timestamp string & flag denoting change from a previous timestamp.
def checkTimestamp(filepath):
  changed = False
  ts = os.stat(filepath).st_mtime
  if filepath in _timestamps:
    changed = ts != _timestamps[filepath]
  _timestamps[filepath] = ts
  return ts, changed
