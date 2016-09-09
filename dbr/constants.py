# -*- coding: utf-8 -*-


### Version information ###
RELEASE = 1
ver_maj = 0
ver_min = 7
ver_rel = 11

# For testing release
if (not RELEASE):
    ver_rel -= 0.5

VERSION = (ver_maj, ver_min, ver_rel)
VERSION_STRING = u'{}.{}.{}'.format(ver_maj, ver_min, ver_rel)

### Website & hosting information ###
HOMEPAGE = u'http://debreate.sourceforge.net/'
gh_project = u'https://github.com/AntumDeluge/debreate'
sf_project = u'https://sourceforge.net/projects/debreate'
