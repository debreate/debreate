## Debreate - Debian Package Builder

#### A graphical program for building Debian (.deb) packages. Package applications, media, artwork, etc.

(http://debreate.sourceforge.net/)

To run launch file named "launch.py" (it should execute via mouse-click as well):
* ./init.py
* or
* python init.py

The source uses a generic Makefile for "building" (because I don't know how to use [GNU Autotools][gnu-autotools] or [CMake][cmake] very well. The source is not actually built. Just open a terminal in the root directory & type 'make install'. To create a distribution package type 'make dist'.


Debreate needs these packages installed to run:
* [python][]
    * Version 2.7 is supported. The goal is to port it to Python 3.
* [wxpython (python-wxgtk)][python-wxgtk2.8]
    * python-wxgtk2.8 is supported by Debreate. For systems newer than [wily][ubu.wily.python-wxgtk] backports will need to be enabled or a wily repository mirror will have to be added to /etc/apt/sources.list.
    * It is planned to port it to [python-wxgtk3][]
* [python-wxversion][]
* [dpkg][]
    * If you are running a Debian/Ubuntu based system, then this is most likely already installed.
* [fakeroot][]
* [coreutils][]


Debreate recommends these packages to be installed:
* [gvfs-bin][]
* [lintian][]




[coreutils]: http://packages.ubuntu.com/coreutils
[dpkg]: http://packages.ubuntu.com/dpkg
[fakeroot]: http://packages.ubuntu.com/fakeroot
[gvfs-bin]: http://packages.ubuntu.com/gvfs-bin
[lintian]: http://packages.ubuntu.com/lintian
[python]: http://packages.ubuntu.com/python2.7
[python-wxversion]: http://packages.ubuntu.com/python-wxversion
[python-wxgtk2.8]: http://packages.ubuntu.com/python-wxgtk2.8
[python-wxgtk3]: http://packages.ubuntu.com/python-wxgtk3

[ubu.wily.python-wxgtk]: http://packages.ubuntu.com/wily/python-wxgtk2.8

[cmake]: https://cmake.org/
[gnu-autotools]: https://en.wikipedia.org/wiki/GNU_Build_System
