
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import errno
import types

from libdbr.logger import getLogger


__logger = getLogger()

__tasklist = {}
__completed = []

## Creates a new runnable task.
#
#  @param name
#    Task identifier.
#  @param action
#    Function to call for task.
def add(name, action):
  action_type = type(action)
  if action_type != types.FunctionType:
    msg = "task action must be a function ({}), found {}".format(name, action_type)
    __logger.error(msg)
    raise TypeError(msg)
    return
  if name in __tasklist:
    __logger.warn("overwriting task ({})".format(name))
  __tasklist[name] = action

## Removes a task from the task list.
#
#  @param name
#    Task identifier.
def remove(name):
  if name not in __tasklist:
    __logger.warn("task not found ({}), not removing".format(name))
    return
  del __tasklist[name]

## Retrieves a task.
#
#  @param name
#    Task identifier.
#  @return
#    Task action or none if not found.
def get(name):
  if name in __tasklist:
    return __tasklist[name]
  return None

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
  if not name in __tasklist:
    __logger.error("invalid task ({}), not running".format(name))
    return errno.ENOENT
  if name in __completed:
    __logger.warn("not re-running task ({})".format(name))
    return 0
  res = __tasklist[name](*args, **kwargs)
  res_type = type(res)
  if res_type != int:
    msg = "invalid return type from task ({}): {}".format(name, res_type)
    __logger.error(msg)
    raise TypeError(msg)
    return 1
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
