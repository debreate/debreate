# -*- coding: utf-8 -*-

## \package globals.application

# MIT licensing
# See: docs/LICENSE.txt


import wx

from globals.paths import ConcatPaths
from globals.paths import PATH_bitmaps


# *** Application information *** #

## Debreate's main homepage
APP_homepage = u'https://antumdeluge.github.io/debreate-web/'

## The old SF homepage
APP_homepage_sf = u'http://debreate.sourceforge.net/'

## GitHub project page
APP_project_gh = u'https://github.com/AntumDeluge/debreate'

## Sourceforge project page
APP_project_sf = u'https://sourceforge.net/projects/debreate'

## Application's logo
APP_logo = wx.Icon(ConcatPaths((PATH_bitmaps, u'icon/64/logo.png')), wx.BITMAP_TYPE_PNG)

## Name of application
APP_name = u'Debreate'


# *** Version information *** #

VERSION_maj = 0
VERSION_min = 8
VERSION_rel = 0
VERSION_tuple = (VERSION_maj, VERSION_min, VERSION_rel)
VERSION_string = u'{}.{}.{}'.format(VERSION_maj, VERSION_min, VERSION_rel)

# Development version: Increment for every development release
VERSION_dev = 1
if VERSION_dev:
    VERSION_string = u'{}-dev{}'.format(VERSION_string, VERSION_dev)


# *** Author information *** #

## Author's email
AUTHOR_email = u'antumdeluge@gmail.com'

## Application's author
AUTHOR_name = u'Jordan Irwin'
