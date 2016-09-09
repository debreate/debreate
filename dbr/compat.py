# -*- coding: utf-8 -*-


# This module creates compatibility between wx versions 2.8 & 3.0

from wximports import wxMAJOR_VERSION


if (wxMAJOR_VERSION == 2):
	print('2.0 compatibility')
elif (wxMAJOR_VERSION == 3):
	print('3.0 compatibility')
else:
	# FIXME: Throw error
	print('incompatible wxWidgets version')
