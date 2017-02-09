# -*- coding: utf-8 -*-

## \package dbr.colors

# MIT licensing
# See: docs/LICENSE.txt


from wx import Colour as Color


## Color used for tooltip backgrounds (yellow)
#
#  FIXME: Unused?
COLOR_tooltip = Color(255, 255, 0)

## Color used for warnings (red-orange)
COLOR_warn = Color(255, 143, 115)

## Color used for errors (red)
COLOR_error = Color(255, 0, 0)

## Text color of executable files (red)
COLOR_executable = COLOR_error
