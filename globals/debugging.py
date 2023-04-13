
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.debugging
#
#  Helper functions for printing debugging messages to terminal

import inspect


## Retrieves line number of script
def lineno():
  return inspect.currentframe().f_back.f_lineno


## Prints a message to the terminal
#
#  \param message
#  \b \e string : Text do be output
#  \param mode
#  \b \e string : Message prefix printed in all capitals
#  \param script
#  \b \e string : Name of script from where function is being called
#  \param line
#  \b \e int : Line number of script where function is being called
#  \param newline
#  \b \e bool : If True, prepends an empty newline to printed message
def HelperMessage(message, mode, script=None, line=None, newline=True):
  if script:
    if line:
      script = "{}:{}".format(script, line)

    message = "[{}] {}".format(script, message)

  message = "{}: {}".format(mode.upper(), message)

  if newline:
    message = "\n{}".format(message)

  print(message)


## Prints a DEBUG message to the terminal
#
#  \param message
#  \b \e string : Text do be output
#  \param script
#  \b \e string : Name of script from where function is being called
#  \param line
#  \b \e int : Line number of script where function is being called
#  \param newline
#  \b \e bool : If True, prepends an empty newline to printed message
def DebugMessage(message, script=None, line=None, newline=True):
  HelperMessage(message, "DEBUG", script, line, newline)


## Prints a FIXME message to the terminal
#
#  \param message
#  \b \e string : Text do be output
#  \param script
#  \b \e string : Name of script from where function is being called
#  \param line
#  \b \e int : Line number of script where function is being called
#  \param newline
#  \b \e bool : If True, prepends an empty newline to printed message
def FixmeMessage(message, script=None, line=None, newline=True):
  HelperMessage(message, "FIXME", script, line, newline)


## Prints a TODO message to the terminal
#
#  \param message
#  \b \e string : Text do be output
#  \param script
#  \b \e string : Name of script from where function is being called
#  \param line
#  \b \e int : Line number of script where function is being called
#  \param newline
#  \b \e bool : If True, prepends an empty newline to printed message
def TodoMessage(message, script=None, line=None, newline=True):
  HelperMessage(message, "TODO", script, line, newline)
