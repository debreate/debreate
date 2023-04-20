
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Tasks execution & management.
#
#  @module libdbr.tasks

import errno
import types

from .logger import Logger


__logger = Logger(__name__)

__tasklist = {}
__completed = []

## Creates a new runnable task.
#
#  @param name
#    Task identifier.
#  @param action
#    Function to call for task.
def add(name, action, desc=None):
  action_type = type(action)
  if action_type != types.FunctionType:
    msg = "task action must be a function ({}), found {}".format(name, action_type)
    __logger.error(msg)
    raise TypeError(msg)
    return
  if name in __tasklist:
    __logger.warn("overwriting task ({})".format(name))
  __tasklist[name] = {"action": action, "desc": desc}

## Removes a task from the task list.
#
#  @param name
#    Task identifier.
def remove(name):
  if name not in __tasklist:
    __logger.warn("task not found ({}), not removing".format(name))
    return
  del __tasklist[name]

## Retrieves a task or the task list.
#
#  @param name
#    Task identifier.
#  @return
#    Task action or none if not found or task list if name not specified.
def get(name=None):
  if name != None and name not in __tasklist:
    msg = "invalid task ({})".format(name)
    __logger.error(msg)
    raise TypeError(msg)
    return None
  if name in __tasklist:
    return __tasklist[name]["action"]
  # make a copy of the task list
  return dict(__tasklist)

## Retrieves available tasks.
#
#  @return
#    List of task names.
def getNames():
  return tuple(__tasklist)

## Runs a task.
#
#  @param name
#    Task identifier.
#  @param args
#    Positional arguments to pass to task.
#  @param kwargs
#    Keyword args to pass to task.
#  @return
#    Error result from running task.
def run(name, *args, **kwargs):
  if type(name) in (list, tuple):
    for n in name:
      res = run(n, *args, **kwargs)
      if res != 0:
        return res
    return 0
  if not name in __tasklist:
    __logger.error("invalid task ({}), not running".format(name))
    return errno.ENOENT
  if name in __completed:
    __logger.warn("not re-running task ({})".format(name))
    return 0
  res = __tasklist[name]["action"](*args, **kwargs)
  # allow returning none to be same as no error
  if res == None:
    res = 0
  res_type = type(res)
  if res_type != int:
    msg = "invalid return type from task ({}): {}".format(name, res_type)
    __logger.error(msg)
    raise TypeError(msg)
    return 1 # FIXME: code isn't processed past an exception error
  return res

## Removes task from completed list so can be re-run.
#
#  @param name
#    Task identifier.
def reset(name):
  if not name in __tasklist:
    __logger.error("invalid task ({}), not resetting".format(name))
    return
  if not name in __completed:
    __logger.warn("task not completed ({}), not resetting".format(name))
    return
  __completed.pop(__completed.index(name))
  if name in __completed:
    __logger.error("an unknown error occurred, task not reset")

## Clears completed list so tasks can be rerun.
def resetAll():
  for idx in reversed(range(len(__completed))):
    __completed.pop(idx)
  if len(__completed) > 0:
    __logger.error("an unknown error occurred, task list not empty")
