
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.md5

import os

from dbr.language  import GT
from globals.ident import chkid
from globals.ident import pgid
from libdbr.fileio import writeFile
from libdbr.logger import Logger
from libdbr.misc   import generateMD5Hash
from ui.dialog     import ErrorDialog
from wiz.helper    import GetField
from wiz.helper    import GetMainWindow


logger = Logger(__name__)

## Creates a file of md5 hashes for files within the staged directory
#
#  @param stage_dir
#    Temporary directory to scan files into list.
#  @param parent
#    The window to be parent of error messages
#  @fixme
#    Should binary files be handled differently?
def WriteMD5(stage_dir, parent=None):
  temp_list = []
  md5_list = [] # Final list used to write the md5sum file
  for ROOT, DIRS, FILES in os.walk(stage_dir):
    # Ignore the 'DEBIAN' directory
    if os.path.basename(ROOT) == "DEBIAN":
      continue

    for F in FILES:
      F = "{}/{}".format(ROOT, F)
      md5 = generateMD5Hash(F)
      logger.debug("{}: {}".format(WriteMD5.__name__, md5))
      temp_list.append(md5)

  for item in temp_list:
    # Remove [stage_dir] from the path name in the md5sum so that it has a
    # true unix path
    # e.g., instead of "/myfolder_temp/usr/local/bin", "/usr/local/bin"
    sum_split = item.split("{}/".format(stage_dir))
    sum_join = "".join(sum_split)
    md5_list.append(sum_join)

  # Create the md5sums file in the "DEBIAN" directory
  # NOTE: lintian ignores the last character of the file, so should end with newline character (\n)
  return writeFile("{}/DEBIAN/md5sums".format(stage_dir), "{}\n".format("\n".join(md5_list)))
