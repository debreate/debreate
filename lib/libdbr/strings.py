
# ****************************************************
# * Copyright © 2023 - Jordan Irwin (AntumDeluge)    *
# ****************************************************
# * This software is licensed under the MIT license. *
# * See: LICENSE.txt for details.                    *
# ****************************************************

# string handling


## Convert an object to string.
#
#  @param obj
#    Object to be converted.
#  @param sep
#    Separation delimiter in case of obj being a list type.
#  @return
#    String containing string representations of vales in list.
def toString(obj, sep=""):
  res = ""
  if type(obj) in (list, tuple, dict):
    for i in obj:
      if res:
        res += sep
      res += str(i)
  else:
    res = str(obj)
  return res
