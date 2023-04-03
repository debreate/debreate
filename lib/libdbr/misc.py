
# ****************************************************
# * Copyright (C) 2023 - Jordan Irwin (AntumDeluge)  *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: docs/LICENSE.txt for details.               *
# ****************************************************

# miscellaneous functions

import hashlib



## Creates a hash from string or bytes data.
#
#  @param data
#    String or bytes data to process.
#  @return
#    MD5 hex hash string.
def generateMD5Hash(data):
  if type(data) == str:
    data = data.encode()
  tmp = hashlib.md5()
  tmp.update(data)
  return tmp.hexdigest()
