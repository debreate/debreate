
# ******************************************************
# * Copyright © 2016-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module dbr.colors

from wx import Colour as Color


## Color used for tooltip backgrounds (yellow).
#
#  @todo
#    FIXME: Unused?
COLOR_tooltip = Color(255, 255, 0)

## Color used for warnings (red-orange).
COLOR_warn = Color(255, 143, 115)

## Color used for errors (red).
COLOR_error = Color(255, 0, 0)

## Text color of executable files (red).
COLOR_executable = COLOR_error

## Text color of symbolic links (green).
COLOR_link = Color(76, 153, 0)

## Text color of directories (blue).
COLOR_dir = Color(0, 0, 255)
