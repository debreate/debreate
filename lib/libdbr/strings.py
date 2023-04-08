
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


__sgrstyles = {
  "end": 0,
  "bold": 1,
  "faint": 2,
  "em": 3,
  "ital": 3,
  "under": 4,
  "sblink": 5,
  "rblink": 6,
  "invert": 7,
  "conceal": 8,
  "xout": 9,
  "pfont": 10,
  "fraktur": 20,
  "dunder": 21,
  "/bold": 22,
  "/faint": 22,
  "/em": 23,
  "/ital": 23,
  "/fraktur": 23,
  "/under": 24,
  "/blink": 25,
  # 26?
  "/invert": 27,
  "/conceal": 28,
  "/xout": 29,
  # 38 TODO: set custom color with '5;<n>' or '2;<r>;<g>;<b>'
  "/fg": 39,
  # 48 TODO: same as 38
  "/bg": 49,
  # 50?
  "frame": 51,
  "circle": 52,
  "over": 53,
  "/frame": 54,
  "/circle": 54,
  "/over": 55
  # more?
}

for _idx in range(1, 10):
  __sgrstyles["afont{}".format(_idx)] = _idx + 10
for _idx in range(1, 9):
  __sgrstyles["fg{}".format(_idx)] = _idx + 29
for _idx in range(1, 9):
  __sgrstyles["bg{}".format(_idx)] = _idx + 39

## Formats a stylized string for terminal output.
#
#  @param st
#    String to be formatted.
#  @return
#    String formatted using ANSI escape codes (Select Graphic Rendition).
def sgr(st):
  for key in __sgrstyles:
    st = st.replace("<{}>".format(key), "\033[{}m".format(__sgrstyles[key]))
  return st
