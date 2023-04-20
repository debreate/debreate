
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Command execution functions.
#
#  @module libdbr.bin

import subprocess


## Creates a uniform agument list.
#
#  @param args
#    List of arguments.
#  @return
#    List of strings.
def __parseArgsList(args):
  args_list = []
  for a in args:
    a_type = type(a)
    if a_type in (list, tuple):
      args_list += __parseArgsList(a)
    elif a_type == str:
      args_list.append(a)
    else:
      raise TypeError("incompatible argument type passed to {} ({})"
          .format(__name__ + "." + execute.__name__, a_type))
  return args_list

## Executes a command.
#
#  @param cmd
#    File to be executed.
#  @param args
#    Arguments to pass to command.
#  @param check
#    Throw an error if command returned non-zero.
#  @param usestderr
#    Use output of stderr if stdout is empty.
#  @return
#    Program exit code & output.
def execute(cmd, *args, check=False, usestderr=False):
  res = subprocess.run([cmd] + __parseArgsList(args), check=check, stdout=subprocess.PIPE,
      stderr=subprocess.PIPE)
  output = res.stdout
  if not output and usestderr:
    output = res.stderr
  if output:
    output = output.decode("utf-8").rstrip()
  return res.returncode, output
