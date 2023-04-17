
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.stage

import os
import shutil

from globals.dateinfo import GetDate
from globals.dateinfo import dtfmt
from libdebreate      import appinfo


## Creates a directory for storing temporary files.
#
#  @return
#    Path to new stage directory, or None if failed.
def CreateStage():
  stage = "/tmp"

  # Use current working directory if no write access to /tmp
  if not os.access(stage, os.W_OK):
    stage = os.getcwd()

  #suffix = "{}{}{}_".format(GetYear(), GetMonthInt(), GetDayInt())

  #suffix = "_temp"
  suffix = GetDate(dtfmt.STAMP)

  stage = "{}/{}-{}_{}".format(stage, appinfo.getName().lower(), appinfo.getVersionString(), suffix)

  if os.access(os.path.dirname(stage), os.W_OK):
    # Start with fresh directory
    if os.path.isdir(stage):
      shutil.rmtree(stage)

    elif os.path.isfile(stage):
      os.remove(stage)

    os.makedirs(stage)

    if os.path.isdir(stage):
      return stage


## Remove a previously created stage directory.
#
#  @param stage
#    Absolute path to directory to remove.
#  @return
#    `True` if stage does not exist.
def RemoveStage(stage):
  if os.access(stage, os.W_OK):
    shutil.rmtree(stage)
  return not os.path.exists(stage)
