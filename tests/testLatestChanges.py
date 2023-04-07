
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

import os

from libdbr      import paths
from libdbr.misc import getLatestChanges


def init():
  changelog = paths.join(paths.getAppDir(), "docs/changelog.txt")
  assert os.path.isfile(changelog)
  changes = getLatestChanges(changelog).split("\n")
  assert len(changes) > 0
  for li in changes:
    assert li.strip() != ""
