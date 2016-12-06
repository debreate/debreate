## Debreate - Debian Package Builder

#### A graphical program for building Debian (.deb) packages. Package applications, media, artwork, etc.

(http://debreate.sourceforge.net/)

To run, launch the file named "init.py" (it should execute via mouse-click as well):
* './init.py' or 'python init.py'

The source uses a generic Makefile for "building" (because I don't know how to use [GNU Autotools][gnu-autotools] or [CMake][cmake] very well). The source is not actually built, but the Makefile simply installs the scripts onto the system. Just open a terminal in the root directory & type 'make install'. To create a distribution package type 'make dist'. To uninstall type 'make uninstall'.

If you have [debuild][] installed, you can run 'make deb-bin' (or 'make deb-bin-signed') from the command line to build the debian package (.deb).


Debreate needs these packages installed to run:
* [python][]
    * Version 2.7 is supported. The goal is to port it to Python 3.
* [wxpython (python-wxgtk)][python-wxgtk3]
    * python-wxgtk3 & [python-wxgtk2.8][] are supported.
* [python-wxversion][]
* [dpkg][]
    * If you are running a Debian/Ubuntu based system, then this is most likely already installed.
* [fakeroot][]
* [coreutils][]


Debreate recommends these packages to be installed:
* [gvfs-bin][]
* [lintian][]


It is recommended to build the .deb package with 'make deb-bin' & install via the system's package manager.




[coreutils]: http://packages.ubuntu.com/coreutils
[debuild]: http://packages.ubuntu.com/debuild
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
