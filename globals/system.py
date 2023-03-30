## \package globals.system

# MIT licensing
# See: docs/LICENSE.txt


import os, sys, wx

from importlib import import_module

from dbr.containers  import Contains
from globals.fileio  import ReadFile
from globals.fileio  import WriteFile
from globals.paths   import getCacheDir
from globals.remote  import GetRemotePageText
from globals.strings import RemoveEmptyLines
from globals.strings import StringIsVersioned


mimport = import_module


# *** Python Info *** #
PY_VER_MAJ = sys.version_info[0]
PY_VER_MIN = sys.version_info[1]
PY_VER_REL = sys.version_info[2]
PY_VER_STRING = "{}.{}.{}".format(PY_VER_MAJ, PY_VER_MIN, PY_VER_REL)


# *** wxWidgets Info *** #

WX_VER_STRING = wx.__version__


# *** Operating System Info *** #

def GetOSInfo(key, upstream=False):
  lsb_release = "/etc/lsb-release"

  if upstream:
    lsb_release = "/etc/upstream-release/lsb-release"

  if not os.path.isfile(lsb_release):
    return None

  release_data = ReadFile(lsb_release, split=True)

  value = None

  for L in release_data:
    if L.startswith(key):
      value = L.replace("{}=".format(key), "").replace("\"", "")
      break

  return value


OS_name = GetOSInfo("DISTRIB_ID")
OS_version = GetOSInfo("DISTRIB_RELEASE")
OS_codename = GetOSInfo("DISTRIB_CODENAME")

OS_upstream_name = GetOSInfo("DISTRIB_ID", True)
OS_upstream_version = GetOSInfo("DISTRIB_RELEASE", True)
OS_upstream_codename = GetOSInfo("DISTRIB_CODENAME", True)

## File where distribution code names cache is stored
FILE_distnames = os.path.join(getCacheDir(), "distnames")

## Retrieves distribution names from remote Debian site
#
#  NOTE: If site layout changes, function will need updated
#  \param obsolete
#  Include obsolete distributions
#  \param unstable
#  Include testing & unstable distributions
#  \param generic
#  Include generic names 'oldstable', 'stable', 'testing', & 'unstable'
def _get_debian_distnames(unstable=True, obsolete=False, generic=False):
  ref_site = "https://wiki.debian.org/DebianReleases"

  # Names added statically are continually used by Debian project
  dist_names = []

  if generic:
    if unstable:
      dist_names.append("unstable")
      dist_names.append("testing")

    dist_names.append("stable")

    if obsolete:
      dist_names.append("oldstable")

  # NOTE: 'stretch' & 'sid' names are repeatedly used for testing & unstable,
  #     but this could change in the future.
  if unstable:
    dist_names.append("sid")
    dist_names.append("stretch")

  page_html = GetRemotePageText(ref_site).split("\n")

  if page_html:
    # Only add up to max_dists to list
    max_dists = 6
    dists_added = 0

    for INDEX in range(len(page_html)):
      LINE = page_html[INDEX].lower()

      if "<p class=\"line862\">" in LINE and LINE.strip().endswith("</td>"):
        stable_version = LINE.split("</td>")[0].split(">")[-1].strip()

        if StringIsVersioned(stable_version):
          dist_names.append(page_html[INDEX+1].split("</a>")[0].split(">")[-1].lower().strip())
          dists_added += 1

          if dists_added >= max_dists:
            break

          # First name found should be current stable version
          if not obsolete:
            break

  return dist_names


## Retrieves distribution names from remote Ubuntu site
#
#  NOTE: If site layout changes, function will need updated
def _get_ubuntu_distnames(unstable=True, obsolete=False):
  ref_site = "https://wiki.ubuntu.com/Releases"
  page_html = GetRemotePageText(ref_site).split("\n")

  dist_names = []
  current = []

  if unstable:
    future = []

  if obsolete:
    eol = []

  if page_html:
    for INDEX in range(len(page_html)):
      LINE = page_html[INDEX].lower()

      if "id=\"current\"" in LINE and len(current) < 2:
        current.append(INDEX + 8)

        continue

      if "id=\"future\"" in LINE:
        if len(current) < 2:
          current.append(INDEX)

        if unstable and len(future) < 2:
          future.append(INDEX + 8)

        continue

      if "id=\"end_of_life\"" in LINE:
        if unstable and len(future) < 2:
          future.append(INDEX)

        if obsolete and len(eol) < 2:
          eol.append(INDEX + 8)
          eol.append(len(page_html) - 1)

          break

    # Lines containing these strings will be ignored
    skip_lines = (
      "releasenotes",
      "class=\"http",
      )

    # Add names in order of newest first

    if unstable and len(future) > 1:
      future = page_html[future[0]:future[1]]

      for LINE in future:
        LINE = LINE.lower()

        if "class=\"line891\"" in LINE and not Contains(LINE, skip_lines):
          name = LINE.split("</a>")[0].split(">")[-1].strip().split(" ")[0]

          if name and name not in dist_names:
            dist_names.append(name)

    if len(current) > 1:
      current = page_html[current[0]:current[1]]

      for LINE in current:
        LINE = LINE.lower()

        if "class=\"line891\"" in LINE and not Contains(LINE, skip_lines):
          name = LINE.split("</a>")[0].split(">")[-1].strip().split(" ")[0]
          if name and name not in dist_names:
            dist_names.append(name)

    if obsolete and len(eol) > 1:
      eol = page_html[eol[0]:eol[1]]

      # Maximum number of obsolete dists that will be added
      eol_max = 6
      eol_added = 0

      for LINE in eol:
        LINE = LINE.lower()

        if "class=\"line891\"" in LINE and not Contains(LINE, skip_lines):
          name = LINE.split("</a>")[0].split(">")[-1].strip().split(" ")[0]

          if name and name not in dist_names:
            dist_names.append(name)

            eol_added += 1
            if eol_added >= eol_max:
              break

  return dist_names


## Retrieves distribution names from remote Linux Mint site
#
#  NOTE: If site layout changes, function will need updated
def _get_mint_distnames():
  ref_site = "https://www.linuxmint.com/download_all.php"
  page_html = GetRemotePageText(ref_site).split("\n")

  dist_names = []

  if page_html:
    for INDEX in range(len(page_html)):
      LINE = page_html[INDEX].lower()

      if "href=\"release.php?id=" in LINE:
        name = LINE.split("</a>")[0].split(">")[-1].strip()

        if name and not StringIsVersioned(name) and name not in dist_names:
          dist_names.append(name)

  return dist_names


## Creates/Updates list of distribution names stored in user's local directory
#
#  \param deprecated
#  If \b \e True, includes obsolete Ubuntu distributions
#  \return
#  \b \e Boolean value of WriteFile
def UpdateDistNamesCache(unstable=True, obsolete=False, generic=False):
  global FILE_distnames

  debian_distnames = _get_debian_distnames(unstable, obsolete, generic)
  ubuntu_distnames = _get_ubuntu_distnames(unstable, obsolete)
  mint_distnames = _get_mint_distnames()

  section_debian = "[DEBIAN]\n{}".format("\n".join(debian_distnames))
  section_ubuntu = "[UBUNTU]\n{}".format("\n".join(ubuntu_distnames))
  section_mint = "[LINUX MINT]\n{}".format("\n".join(mint_distnames))

  return WriteFile(FILE_distnames, "\n\n".join((section_debian, section_ubuntu, section_mint)))


## Retrieves distribution names from cache file
#
#  \param deprecated
#  If \b \e True, includes obsolete Ubuntu distributions (only works if cache file doesn't already exist)
#  \return
#  ???
def GetCachedDistNames(unstable=True, obsolete=False, generic=False):
  global FILE_distnames

  if not os.path.isfile(FILE_distnames):
    if not UpdateDistNamesCache(unstable, obsolete, generic):
      return None

  text_temp = ReadFile(FILE_distnames)

  dist_names = {}

  if text_temp:
    try:
      dist_names["debian"] = RemoveEmptyLines(text_temp.split("[DEBIAN]")[1].split("[UBUNTU]")[0].split("\n"))

    except IndexError:
      pass

    try:
      dist_names["ubuntu"] = RemoveEmptyLines(text_temp.split("[UBUNTU]")[1].split("[LINUX MINT]")[0].split("\n"))

    except IndexError:
      pass

    try:
      dist_names["mint"] = RemoveEmptyLines(text_temp.split("[LINUX MINT]")[1].split("\n"))

    except IndexError:
      pass

  return (dist_names)


## Get a list of available system release codenames
#
#  FIXME: unstable, obsolete, & generic names should only be added if specified
def GetOSDistNames():
  global FILE_distnames

  dist_names = []

  if os.path.isfile(FILE_distnames):
    cached_names = GetCachedDistNames()

    if cached_names:
      for OS in ("debian", "ubuntu", "mint",):
        for NAME in cached_names[OS]:
          dist_names.append(NAME)

  # Only check system for dist names if could not be loaded from cache file
  if not dist_names:
    # Ubuntu & Linux Mint distributions
    global OS_codename, OS_upstream_codename

    for CN in (OS_codename, OS_upstream_codename,):
      if CN and CN not in dist_names:
        dist_names.append(CN)

    # Debian distributions
    FILE_debian = "/etc/debian_version"
    if os.path.isfile(FILE_debian):
      debian_names = RemoveEmptyLines(ReadFile(FILE_debian, split=True))[:1]

      # Usable names should all be on first line
      if "/" in debian_names[0]:
        debian_names = sorted(debian_names[0].split("/"))

      for NAME in reversed(debian_names):
        if NAME not in dist_names:
          # Put Debian names first
          dist_names.insert(0, NAME)

  return tuple(dist_names)
