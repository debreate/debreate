# -*- coding: utf-8 -*-

import os, gettext

TRANSLATION_DOMAIN = u'debreate'
LOCALE_DIR = os.path.join(os.path.dirname(__file__), u'locale')

gettext.install(TRANSLATION_DOMAIN, LOCALE_DIR)

GT = _
