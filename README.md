
![][icon]

# Debreate - Debian Package Builder


<a name="toc">
<h2>Table of Contents</h2>
</a>

- [Description](#description)
- [Licensing](#licensing)
- [Explanation](#explanation)
- [Requirements](#requirements)
- [Building](#build)
    - [Build Script](#build-script)
    - [Makefile](#build-make)
    - [Building .deb Package](#build-deb)
- [Standalone/Portable](#portable)
- [Usage](#usage)
- [Links](#links)
    - [Project Pages](#links-proj)
    - [Downloads](#links-dl)
    - [Other Pages](#links-other)


<a name="description">
<h2><a href="#toc">Description</a></h2>
</a>

Debreate is a utility to aid in creating [Debian (.deb)][page.deb] packages. Currently it only
supports binary packaging (_note that the term "binary package" is used loosely, as such packages
can contain scripts & non-code items such as media images, audio, & more_) for personal
distribution. Plans for using backends such as [dh_make][home.dh-make] & [debuild][pkg.devscripts]
for creating source packages are in the works. But source packaging can be quite different & is a
must if you want to get your packages into a distribution's official repositories or a
[Launchpad][home.launchpad] [Personal Package Archive (PPA)][page.ppa]. The latter from which
[Debreate is available][ppa.debreate].


<a name="licensing">
<h2><a href="#toc">Licensing</a></h2>
</a>

Debreate & [libdbr][proj.gh.libdbr] are licensed under [MIT](LICENSE.txt).


<a name="explanation">
<h2><a href="#toc">Explanation</a></h2>
</a>

The definition of "Debian source package" may be a little confusing, as it was for me, for those
that are new to the [Debian format][deb-policy], or perhaps new to packaging in general. Debian
source packages are essentially no different than common [tarballed source archives][page.tar] &
they can be available in many of the popular formats such as [Gzip (.tar.gz)][home.gzip],
[BZip2 (.tar.bz2)][home.bzip2], [XZ (tar.xz)][home.xz-utils], [Lzip (tar.lzip)][home.lzip], et al.

To build Debian binary packages (.deb) from source, it must first be "debianized". A source package
can be debianized using one of two methods:

1. __[internal/native][deb-policy.native]:__

    Instructions for the build utilities
    are included within the source package in a directory labelled "debian".

2. __external:__

    Instructions are contained within a separate package distributed alongside the original source.

The debian directory, or package, contains files with instructions & meta data on how the source is
to be patched, compiled, & built into a binary format.

Source packaging is a must for inclusion of software in official repositories or PPAs. The
debianized package is uploaded to repo/PPA host server where it is built into a binary package &
published for release in .deb format. This differs from systems such as [Arch's ABS][bs.arch] &
[FreeBSD's Ports][bs.freebsd] build systems where only the instructions files are stored on the
host server. Downloading of source packages from the upstream maintainer is done as part of the
build process.


<a name="requirements">
<h2><a href="#toc">Requirements</a></h2>
</a>

Debreate requires the following software:

- [Python][home.python] (>=3.10) ([Ubuntu package][pkg.python3])

- [python3-wxgtk-webview4.0](https://packages.ubuntu.com/search?keywords=python3-wxgtk4.0) **(for newer versions of Debian/Ubuntu)**

- [wxPython][home.wxpython] **(>=4.0.7, >=4.2.0 for older versions of Debian/Ubuntu)**
    - Packaged as [_python3-wxgtk*_][pkg.wxpython] on Debian/Ubuntu.
    - Available via [Pypi][pip.wxpython].
- [dpkg][home.dpkg] ([Ubuntu package][pkg.dpkg])
    - If you are running a Debian/Ubuntu based system this is most likely already installed.
- [fakeroot][home.fakeroot] ([Ubuntu package][pkg.fakeroot])

Required for building a Debian distribution package:
- [devscripts][pkg.devscripts] 

These packages are recommended to enable some features:

- [lintian][home.lintian] ([Ubuntu package][pkg.lintian])


<a name="build">
<h2><a href="#toc">Building</a></h2>
</a>

<a name="build-script">
<h3><a href="#toc">Build Script</a></h3>
</a>

The software comes bundled with a _build.py_ script to facilitate the build process & other tasks.
Note that Debreate is written in a [scripting language][page.scripting], so building does not
include any compiling of source code. The build script is used for staging the necessary files into
a directory structure for packaging & installation.

<a name="build-script-usage">
<h4>Script Usage</h4>
</a>

The build script is invoked as `python3 build.py [args]` or `./build.py [args]`.

<a name="build-script-args">
Arguments:
</a>

- `-h|--help`
    - Show help information.
- `-v|--version`
    - Show Debreate version.
- `-V|--verbose`
    - Include detailed task information when printing to stdout.
- `-l|--log-level <level>`
    - Logging output verbosity.
    - Levels are __0__ (__silent__), __1__ (__error__), __2__ (__warn__), __3__ (__info__),
      & __4__ (__debug__).
- `-t|--task <task>`
    - Task to be executed (see [Build Tasks](#build-script-tasks)).
- `-p|--prefix <directory>`
    - Path prefix to directory where files are to be installed.
- `-d|--dir <directory>`
    - Target directory (defaults to system root). This is useful for directing the script to place files
      in a temporary directory rather than the intended installation path. It is equivalent to the
      "[DESTDIR][bs.gnu-destdir]" environment variable used by [GNU make][bs.gnu-make].

<a name="build-script-tasks">
Build Tasks:
</a>

- `stage`
    - Prepare files for installation or distribution.
- `install`
    - Install files to directory specified by `--prefix` argument.
- `uninstall`
    - Uninstall files from directory specified by by `--prefix` argument.
- `dist-source`
    - Build a source distribution package.
- `dist-bin`
    - Build a portable binary .zip distribution package.
- `dist-deb`
    - Build a binary Debian distribution package.
- `clean`
    - Remove all temporary build files.
- `clean-stage`
    - Remove temporary build files from 'build/stage' directory.
- `clean-deb`
    - Remove temporary build files from 'debian' directory.
- `clean-dist`
    - Remove built packages from 'build/dist' directory.
- `update-version`
    - Update relevant files with version information from 'build.conf'.
- `test`
    - Run configured unit tests from 'tests' directory.
- `check-code`
    - Check code with [pylint][proj.pylint] & [mypy][].
- `changes`
    - Print most recent changes from 'doc/changelog' to stdout.


<a name="build-make">
<h3><a href="#toc">Makefile</a></h3>
</a>

A generic [Makefile][page.makefile] is included for building with a GNU compliant [make][page.make]
command. It is simply a wrapper for the targets executed by the `build.py` script. Open a terminal
in the directory where the source code is located & execute `make install` with
[superuser privileges][page.superuser]. To uninstall, execute `make uninstall`. Use the environment
variables `prefix` & `DESTDIR` to control the installation target directory.


<a name="build-deb">
<h3><a href="#toc">Building .deb Package</a></h3>
</a>

If you have [devscripts][pkg.devscripts] installed, you can execute `python3 build.py -t dist-deb` to
build the debian package (.deb). The package will be located in the 'build/dist' directory. To
install execute `dpkg --install build/dist/debreate_\<version\>_all.deb` with
[superuser privileges][page.superuser]. Or open the package with a GUI installer such as
[gdebi][pkg.gdebi] or [QAPT][pkg.qapt].


<a name="portable">
<h2><a href="#toc">Standalone/Portable</a></h2>
</a>

To run without installation simply execute the file named "init.py" (from a terminal `./init.py` or
`python3 init.py`).


<a name="usage">
<h2><a href="#toc">Usage</a></h2>
</a>

Sorry, not up-to-date usage information yet. But you can have a look at this
[old PDF document](https://debreate.sourceforge.net/res/doc/usage_en.pdf) if you like.


<a name="links">
<h2><a href="#toc">Links</a></h2>
</a>


<a name="links-proj">
<h3><a href="#toc">Project Pages</a></h3>

- [Homepage](https://debreate.github.io/)
- [GitHub project][proj.gh]
- [GitLab project][proj.gl]
- [SourceForge project][proj.sf]
- [PPA][ppa.debreate]
- [Development PPA][ppa.debreate-dev]


<a name="links-dl">
<h3><a href="#toc">Downloads</a></h3>
</a>

- [stable](https://github.com/debreate/debreate/releases/latest)
- [latest](https://github.com/debreate/debreate/releases)
- [PPA stable][ppa.debreate]
- [PPA development][ppa.debreate-dev]


<a name="links-other">
<h3><a href="#toc">Other Pages</a></h3>
</a>

- [OpenDesktop](https://www.opendesktop.org/p/1129667)
- [AlternativeTo](https://alternativeto.net/software/debreate/)
- [Open Hub](https://www.openhub.net/p/debreate)


[icon]: bitmaps/icon/64/logo.png

[bs.arch]: https://wiki.archlinux.org/title/Arch_Build_System
[bs.freebsd]: https://www.freebsd.org/ports/
[bs.gnu]: https://www.gnu.org/software/automake/manual/html_node/GNU-Build-System.html
[bs.gnu-destdir]: https://www.gnu.org/prep/standards/html_node/DESTDIR.html
[bs.gnu-make]: https://www.gnu.org/software/make/

[deb-policy]: https://www.debian.org/doc/debian-policy/
[deb-policy.native]: https://www.debian.org/doc/manuals/maint-guide/advanced.en.html#native-dh-make

[home.bzip2]: https://sourceware.org/bzip2/
[home.dh-make]: https://salsa.debian.org/debian/dh-make
[home.dpkg]: https://wiki.debian.org/Teams/Dpkg
[home.fakeroot]: https://salsa.debian.org/clint/fakeroot
[home.gzip]: https://www.gzip.org/
[home.launchpad]: https://launchpad.net/
[home.lintian]: https://lintian.debian.org/
[home.lzip]: https://www.nongnu.org/lzip/
[home.python]: https://python.org/
[home.wxpython]: https://wxpython.org/
[home.xz-utils]: https://tukaani.org/xz/
[mypy]: https://mypy-lang.org/

[page.deb]: https://wikipedia.org/wiki/Deb_(file_format)
[page.make]: https://en.wikipedia.org/wiki/Make_(software)
[page.makefile]: https://wikipedia.org/wiki/Makefile
[page.ppa]: https://wikipedia.org/wiki/Ubuntu#Package_Archives
[page.scripting]: https://wikipedia.org/wiki/Scripting_language
[page.superuser]: https://wikipedia.org/wiki/Superuser
[page.tar]: https://wikipedia.org/wiki/Tar_(computing)

[pip.wxpython]: https://pypi.org/project/wxPython/

[pkg.devscripts]: https://packages.ubuntu.com/devscripts
[pkg.dh-make]: https://packages.ubuntu.com/dh-make
[pkg.dpkg]: https://packages.ubuntu.com/dpkg
[pkg.fakeroot]: https://packages.ubuntu.com/fakeroot
[pkg.gdebi]: https://packages.ubuntu.com/gdebi
[pkg.gvfs-bin]: https://packages.ubuntu.com/gvfs-bin
[pkg.lintian]: http://packages.ubuntu.com/lintian
[pkg.python3]: https://packages.ubuntu.com/python3
[pkg.qapt]: https://packages.ubuntu.com/qapt-deb-installer
[pkg.wxpython]: https://packages.ubuntu.com/python3-wxgtk4.0

[ppa.debreate]: https://launchpad.net/~antumdeluge/+archive/ubuntu/debreate
[ppa.debreate-dev]: https://launchpad.net/~antumdeluge/+archive/ubuntu/debreate-dev

[proj.gh]: https://github.com/debreate/debreate
[proj.gh.libdbr]: https://github.com/debreate/libdbr
[proj.gl]: https://gitlab.com/debreate/debreate
[proj.pylint]: https://github.com/pylint-dev/pylint
[proj.sf]: https://sourceforge.net/projects/debreate
