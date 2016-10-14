## ![Debreate icon][icon] Debreate - Debian Package Builder


### Table of Contents
* [Description](#description)
* [Installation](#installation)
* [Standalone Use](#standalone-use)
* [Links](#links)
* [Other Pages](#other-pages)


### [Description](#table-of-contents)

Debreate is a utility to aid in creating [Debian (.deb)][wiki.deb] packages. Currently it only supports binary packaging which allows packaging of pre-compiled or scripted applications, media, artwork, etc. for personal distribution. Plans for using backends such as [dh_make][pkg.dh-make] & debuild (available in [devscripts][pkg.devscripts] package) for creating source packages are in the works. But source packaging can be quite different & is a must if you want to get your packages into a distribution's official repositories or a [Launchpad][launchpad] [Personal Package Archive (PPA)][wiki.ppa]. The latter from which [Debreate has recently become available][ppa.debreate].

The definition of Debian source packages may be a little confusing (as it was for me) for those that are new to the Debian format, or perhaps packaging in general. Debian source packages are essentially no different than common tarballed source archives & they can be available in many of the popular formats such as Gzip (.tar.gz), BZip2 (.tar.bz2), XZ (tar.xz), Lzip (tar.lzip), etc. To build Debian binary packages from source code, it must first be "debianized". Debianization involves creating a directory called 'debian' within the source root folder. Files with instructions, meta data, & more are placed within to instruct Debian tools, such as 'debuild', on how the source must be compiled & packaged into the final .deb. This is the process that must be taken to host software on repositories such as Lauchpad's PPA system. The debianized source is uploaded, then built & packaged on-site automatically. The resulting binary package (.deb) is published to the target PPA.


### [Installation](#table-of-contents)

The source uses a generic Makefile for "building" (because I don't know how to use [GNU Autotools][gnu-autotools] or [CMake][cmake] very well). The source is not actually built, but the Makefile simply installs the scripts onto the system. Just open a terminal in the root directory & type 'make install'. To create a distribution package type 'make dist'. To uninstall type 'make uninstall'.

If you have [debuild][pkg.devscripts] installed, you can run 'make debuild' from the command line to build the debian package (.deb).


Debreate needs these packages installed to run:
* [python][pkg.python]
    * Version 2.7 is supported. The goal is to port it to Python 3.
* python-wxgtk ([wxPython][wxpython])
    * [python-wxgtk2.8][pkg.python-wxgtk2.8] is supported by Debreate. For Ubuntu systems newer than Wily (15.10), backports will need to be enabled or a [Wily repository mirror][pkg-wily.python-wxgtk2.8] will have to be added to /etc/apt/sources.list.
    * [python-wxgtk3][pkg.python-wxgtk3] support is available in the [unstable development branch][src.debreate-unstable].
* [python-wxversion][pkg.python-wxversion]
* [dpkg][pkg.dpkg]
    * If you are running a Debian/Ubuntu based system, then this is most likely already installed.
* [fakeroot][pkg.fakeroot]
* [coreutils][pkg.coreutils]


These packages are recommended & enable some features:
* [gvfs-bin][pkg.gvfs-bin]
* [lintian][pkg.lintian]


It is recommended to build the .deb package with 'make debuild' & install via the system's package manager.


### [Standalone Use](#table-of-contents)

To run, launch the file named "init.py" (it should execute via mouse-click as well):
* './init.py' or 'python init.py'


### [Links](#table-of-contents)
* [Homepage](http://debreate.sourceforge.net/)
* [Sourceforge Project](https://sourceforge.net/projects/debreate)
* [GitHub Project](https://github.com/AntumDeluge/debreate)
* [PPA][ppa.debreate]


### [Other Pages](#table-of-contents)
* [OpenDesktop](https://www.opendesktop.org/content/show.php?content=101776)
* [FreewareFiles](http://www.freewarefiles.com/Debreate_program_56557.html)
* [alternativeTo](http://alternativeto.net/software/debreate/)



[icon]: bitmaps/debreate64.png

[launchpad]: https://launchpad.net/
[wxpython]: https://wxpython.org/

[wiki.deb]: https://en.wikipedia.org/wiki/Deb_(file_format)
[wiki.ppa]: https://en.wikipedia.org/wiki/Personal_Package_Archive

[src.debreate-unstable]: https://github.com/AntumDeluge/debreate/tree/unstable

[ppa.debreate]: https://launchpad.net/~antumdeluge/+archive/ubuntu/debreate

[pkg.coreutils]: http://packages.ubuntu.com/coreutils
[pkg.devscripts]: http://packages.ubuntu.com/devscripts
[pkg.dh-make]: http://packages.ubuntu.com/dh-make
[pkg.dpkg]: http://packages.ubuntu.com/dpkg
[pkg.fakeroot]: http://packages.ubuntu.com/fakeroot
[pkg.gvfs-bin]: http://packages.ubuntu.com/gvfs-bin
[pkg.lintian]: http://packages.ubuntu.com/lintian
[pkg.python]: http://packages.ubuntu.com/python2.7
[pkg.python-wxversion]: http://packages.ubuntu.com/python-wxversion
[pkg.python-wxgtk2.8]: http://packages.ubuntu.com/python-wxgtk2.8
[pkg.python-wxgtk3]: http://packages.ubuntu.com/python-wxgtk3

[pkg-wily.python-wxgtk2.8]: http://packages.ubuntu.com/wily/python-wxgtk2.8

[cmake]: https://cmake.org/
[gnu-autotools]: https://en.wikipedia.org/wiki/GNU_Build_System
