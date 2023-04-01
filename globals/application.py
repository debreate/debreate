## \package globals.application

# MIT licensing
# See: docs/LICENSE.txt


import os.path
import wx

from globals.paths import getBitmapsDir


# *** Application information *** #
## Debreate's main homepage
APP_homepage = "https://antumdeluge.github.io/debreate-web/"

## The old SF homepage
APP_homepage_sf = "http://debreate.sourceforge.net/"

## GitHub project page
APP_project_gh = "https://github.com/AntumDeluge/debreate"

## Sourceforge project page
APP_project_sf = "https://sourceforge.net/projects/debreate"

## Application's logo
APP_logo = wx.Icon(os.path.join(getBitmapsDir(), "icon", "64", "logo.png"), wx.BITMAP_TYPE_PNG)

## Name of application
APP_name = "Debreate"


# *** Version information *** #

VERSION_maj = 0
VERSION_min = 8
VERSION_rev = 0
VERSION_tuple = [VERSION_maj, VERSION_min]
VERSION_string = "{}.{}".format(VERSION_maj, VERSION_min)
if VERSION_rev > 0:
    VERSION_tuple.append(VERSION_rev)
    VERSION_string += ".{}".format(VERSION_rev)
VERSION_tuple = tuple(VERSION_tuple)

# Development version: Increment for every development release
VERSION_dev = 2
if VERSION_dev:
  VERSION_string = "{}-dev{}".format(VERSION_string, VERSION_dev)


# *** Author information *** #

## Author's email
AUTHOR_email = "antumdeluge@gmail.com"

## Application's author
AUTHOR_name = "Jordan Irwin"
