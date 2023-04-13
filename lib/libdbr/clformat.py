
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

## Command line input formatter.
#
#  @module libdbr.clformat

import argparse
import re


## Formatter class for argument parser.
class Formatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
  description = None

  def _expand_help(self, *args, **kwargs):
    res = super()._expand_help(*args, **kwargs)
    m = re.search(r" \(default: .*\)", res, flags=re.M)
    if m:
      span = m.span()
      _default = res[span[0]:span[1]]
      res = res[:span[0]].replace("\r\n", "\n").replace("\r", "\n").split("\n")
      res[0] = res[0] + _default
      res = "\n".join(res)
    return res

  def format_help(self, *args, **kwargs):
    res = super().format_help(*args, **kwargs)
    if Formatter.description:
      res = Formatter.description + "\n\n" + res
    return res
