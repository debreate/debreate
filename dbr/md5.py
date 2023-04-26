
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.md5

import os

from libdbr        import fileio
from libdbr        import paths
from libdbr.logger import Logger
from libdbr.misc   import generateMD5Hash


logger = Logger(__name__)

## Creates a file of md5 hashes for files within the staged directory
#
#  @param stage_dir
#    Temporary directory to scan files into list.
#  @param parent
#    The window to be parent of error messages
def WriteMD5(stage_dir, parent=None):
  temp_list = []
  md5_list = [] # Final list used to write the md5sum file
  for ROOT, DIRS, FILES in os.walk(stage_dir):
    # Ignore the 'DEBIAN' directory
    if os.path.basename(ROOT) == "DEBIAN":
      continue

    for F in FILES:
      abs_path = paths.join(ROOT, F)
      rel_path = abs_path[len(stage_dir)+1:]
      md5 = generateMD5Hash(fileio.readFile(abs_path, binary=True)) + "  " + rel_path
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
  return fileio.writeFile("{}/DEBIAN/md5sums".format(stage_dir), "{}\n".format("\n".join(md5_list)))
