
# ******************************************************
# * Copyright © 2017-2023 - Jordan Irwin (AntumDeluge) *
# ******************************************************
# * This software is licensed under the MIT license.   *
# * See: LICENSE.txt for details.                      *
# ******************************************************

## @module globals.changes

import globals.dateinfo

from globals.strings import RemoveEmptyLines
from globals.system  import OS_codename
from libdbr          import dateinfo
from libdbr          import strings
from libdbr.dateinfo import dtfmt
from libdbr.logger   import Logger
from libdebreate     import appinfo


__logger = Logger(__name__)

section_delims = "*-+#"

## @todo Doxygen
def _strip_line(line, preserve_indent=False):
  chars = " \t"

  if preserve_indent:
    return line.rstrip(chars)

  return line.strip(chars)


## @todo Doxygen
def _format_section(line, preserve_indent=False):
  global section_delims

  return "  * {}".format(_strip_line(line, preserve_indent).lstrip(" \t{}".format(section_delims)))


## Formats lines for changelog output.
#
#  @todo parameters
def _format_lines(lines, preserve_indent=False):
  if isinstance(lines, tuple):
    lines = list(lines)

  if lines:
    global section_delims

    for INDEX in range(len(lines)):
      if INDEX == 0:
        # First line will always start with an asterix
        lines[INDEX] = _format_section(lines[INDEX], preserve_indent)
        continue

      # Make sure line is not empty before setting section
      if lines[INDEX] and lines[INDEX].lstrip(" \t")[0] in section_delims:
        lines[INDEX] = _format_section(lines[INDEX], preserve_indent)

      else:
        lines[INDEX] = "	{}".format(_strip_line(lines[INDEX], preserve_indent))

  return tuple(lines)


## Formats date & time for changelog.
#
#  @todo return
def _get_cl_timestamp():
  __logger.deprecated(_get_cl_timestamp, alt="libdbr.dateinfo.getDebianizedDate")

  fmt = globals.dateinfo.dtfmt.CL
  return "{} {} {}".format(globals.dateinfo.GetDate(fmt), dateinfo.getTime(dtfmt.CL),
      globals.dateinfo.GetTimeZone(fmt))


## Function to format text Debian changelog standards
#
#  @param text
#    String to be formatted.
#  @return
#    Debian changelog format.
#  @deprecated
#    Use `libdbr.misc.formatDebianChanges`.
def FormatChangelog(text, name=appinfo.getName(), version=appinfo.getVersionString(), dist=OS_codename,
      urgency="low", packager=appinfo.getAuthor(), email=appinfo.getEmail(), preserve_indent=False):
  __logger.deprecated(FormatChangelog, alt="libdbr.misc.formatDebianChanges")

  if strings.isEmpty(text):
    return None

  # Remove leading & trailing whitespace & empty lines & split into
  # list of lines.
  lines = text.strip(" \t\n\r").split("\n")

  if not lines:
    return None

  lines = RemoveEmptyLines(lines)
  lines = _format_lines(lines, preserve_indent)

  text = "\n".join(lines)
  header = "{} ({}) {}; urgency={}\n".format(name, version, dist, urgency)
  footer = "\n -- {} <{}>  {}".format(packager, email, _get_cl_timestamp())

  return "\n".join((header, text, footer))
