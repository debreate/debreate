
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## Threading.
#
#  WARNING: Standard Python module 'threads' cannot be imported here.
#
#  @module globals.threads

import threading

from libdbr.logger import Logger


_logger = Logger(__name__)

__active_threads = {}

# next thread handle
__next_id = 1000

## Handles creating unique thread IDs.
#
#  @return
#    Integer ID.
def __newId():
  global __next_id
  _id = __next_id
  __next_id += 1
  return _id

## Retrieves the active threads.
#
#  @return
#    List of threads.
def getActive():
  return __active_threads

## Checks if a thread is currently active.
#
#  @param t_id
#    Thread integer ID.
#  @return
#    `True` if thread is in active list & `is_alive` flag set.
def isActive(t_id):
  return t_id in __active_threads and __active_threads[t_id].is_alive()

## Creates a new thread for processing.
#
#  @return
#    Integer ID of new thread & new thread.
def create(func, *args, start=True, **kwargs):
  t_id = __newId()
  # create a new thread & start it
  __active_threads[t_id] = threading.Thread(target=func, args=args, kwargs=kwargs)
  if start:
    __active_threads[t_id].start()
  _logger.debug("created new thread '{}' (registered: {})".format(t_id, len(__active_threads)))
  return t_id

## Creates a new thread for processing.
#
#  @return
#    Integer ID if of new thread.
#  @deprecated
#    Use `threads.create`.
def CreateThread(func, *args, **kwargs):
  _logger.deprecated(CreateThread, alt=create)

  return create(func, *args, **kwargs)

## Starts a thread in the active list.
#
#  @param t_id
#    Thread integer ID.
def start(t_id):
  if t_id not in __active_threads:
    _logger.warn("thread '{}' not found, cannot start".format(t_id))
    return
  t = __active_threads[t_id]
  if t.is_alive():
    _logger.warn("thread '{}' is already active".format(t_id))
    return
  _logger.debug("starting thread '{}'".format(t_id))
  t.start()

## Ends an active thread.
#
#  @param t_id
#    Integer ID of the thread to end.
#  @return
#    `True` if thread was successfully ended.
def end(t_id):
  if t_id not in __active_threads:
    _logger.debug("thread '{}' not active".format(t_id))
    return True
  t = __active_threads[t_id]
  if not t.is_alive():
    _logger.debug("removing dead thread '{}'".format(t_id))
  else:
    _logger.debug("joining thread '{}'".format(t_id))
    t.join()
  del __active_threads[t_id]
  return not t.is_alive() and t_id not in __active_threads

## Ends an active thread.
#
#  @param t_id
#    Integer ID of the thread to kill.
#  @return
#    `True` if thread was successfully killed.
#  @deprecated
#    Use `threads.end`.
def KillThread(t_id):
  _logger.deprecated(KillThread, alt=end)

  return end(t_id)
