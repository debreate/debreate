
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import os
import sys

from libdbr import paths


def init():
  a = "foo"; b = "bar"; c = "baz"
  subject = a + os.sep + b + os.sep + c

  assert paths.join(a, b, c) == subject
  assert paths.join((a, b, c)) == subject
  assert paths.join([a, b, c]) == subject
  assert paths.join(subject) == subject
  assert paths.join(a, (b, c)) == subject
  assert paths.join((a, b), c) == subject
  assert paths.join(a, [b, c]) == subject
  assert paths.join([a, b], c) == subject
  assert paths.join(a + b + c) == "foobarbaz"
  assert paths.join(a + b, c) == "foobar" + os.sep + "baz"
  assert paths.join() == "."
