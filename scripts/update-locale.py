#! /usr/bin/env python
# -*- coding: utf-8 -*-

# TODO: This script is incomplete


import os, sys, errno
from commands import getstatusoutput
from scripts_globals import root_dir, required_locale_files, \
    GetInfoValue

# Updates the 'locale/debreate.pot' file
def UpdateMain():
    pass

for F in required_locale_files:
    if not os.path.isfile(F):
        print('[ERROR] Required file not found: {}'.format(F))
        sys.exit(errno.ENOENT)


PACKAGE = GetInfoValue('NAME')
AUTHOR = GetInfoValue('AUTHOR')
EMAIL = GetInfoValue('EMAIL')
VERSION = GetInfoValue('VERSION')

# Format
gt_language = '--language=Python'
gt_coding = '--from-code=UTF-8'
gt_keyword = '--keyword=GT -k'

# Package
gt_author = '--copyright-holder="{}"'.format(AUTHOR)
gt_package = '--package-name={}'.format(PACKAGE.title())
gt_version = '--package-version={}'.format(VERSION)
gt_email = '--msgid-bugs-address={}'.format(EMAIL)

# Output
gt_domain = '--default-domain={}'.format(PACKAGE.lower())
gt_directory = '--directory="{}"'.format(root_dir)
gt_output = '-o -'

# Misc
gt_other = '--no-location --no-wrap --sort-output'

# Input
gt_original = '--exclude-file=locale/debreate.pot'
gt_input = 'init.py'


args_format = ' '.join((gt_language, gt_coding, gt_keyword))
args_package = ' '.join((gt_author, gt_package, gt_version, gt_email))
args_output = ' '.join((gt_domain, gt_directory, gt_output))
args_misc = gt_other
args_input = ' '.join((gt_original, gt_input))

cmd_gt = 'xgettext {} {} {} {} {}'.format(
    args_format, args_package, args_output,
    args_misc, args_input
    )

cmd_output = getstatusoutput(cmd_gt)
cmd_code = cmd_output[0]
cmd_output = cmd_output[1]

print('[DEBUG]\n\tCommand: {}\n\tExit code: {}\n\tOutput: {}'.format(cmd_gt, cmd_code, cmd_output))
