
###############################################################################
# - S1 - CONTENTS ----------------------------------------------------------- #
###############################################################################

# CONTENTS:
‣ CONTENTS .............................................. S1
‣ LICENSE ............................................... S2
‣ ABOUT ................................................. S3
‣ REQUIREMENTS .......................................... S4
  • Python Interpreter ................................. 4.1
  • Libraries .......................................... 4.2
    ◦ wxWidgets/wxPython ............................. 4.2.1
  • System ............................................. 4.3
    ◦ OS ............................................. 4.3.1
    ◦ Required Components ............................ 4.3.2
    ◦ Optional Components ............................ 4.3.3
‣ Installing ............................................ S5
  • Source ............................................. 5.1
  • Binary ............................................. 5.2
    ◦ Debian Package ................................. 5.2.1
    ◦ Tarballed Package .............................. 5.2.2
‣ Planned Features ...................................... S6
  
  
###############################################################################
# - S2 - LICENSE ------------------------------------------------------------ #
###############################################################################
  
  Debreate & its source code are copyright Jordan Irwin 2010-2014 & are
  distributed under the terms & conditions of the GNU General Public
  License (GPL) version 3. See "license-GPL3.txt" for more information.
  
  
###############################################################################
# - S3 - ABOUT -------------------------------------------------------------- #
###############################################################################
  
  Debreate is a utility to aid in building Debian packages (.deb). The goal is
  to make packaging for Debian based Linux distributions more appealing with an
  easy to use interface for creating distributable archives of applications,
  artwork, media, and more.
  
  
###############################################################################
# - S4 - REQUIREMENTS ------------------------------------------------------- #
###############################################################################
  
_______________________________________________________________________________
- S4.1 - Python Interpreter --
  

_______________________________________________________________________________
- S4.2 - Libraries --
  
- S4.2.1 - wxWidgets/wxPython:
  
  The source code is written in C++ syntax so a C++ compiler is required for
  building. The project has been built & tested with the GNU Compiler
  Collection (GCC) & GNU/BSD make. Other compilers may be compatible but have
  not been tested so included instructions will mostly be limited to GCC.
  
  
_______________________________________________________________________________
# S4.3 - System --
  
- S4.3.1 - OS:
  
  
- S4.3.2 - Required Components:
  
  
- S4.3.3 - Optional Components:
  
  
  
###############################################################################
# - S5 - INSTALLING --------------------------------------------------------- #
###############################################################################
  
_______________________________________________________________________________
- S5.1 - Source --
  
  The source from SVN comes with a Makefile. To install open a terminal and
  navigate into the source's root directory. Execute "make install" or "make
  uninstall". Optionally the DESTDIR variable can be set from the command line.
  For help execute "make help".
  
  		make install
  		make uninstall
  
  or
  
  		make install DESTDIR=<path>
  		make uninstall DESTDIR=<path>
  
  Make sure that DESTDIR is the same for both "install" & "uninstall", else
  uninstallation will fail.
  
_______________________________________________________________________________
- S5.2 - Binary --
  
- S5.2.1 - Debian Package:
  
  
- S5.2.2 - Tarballed Package:
  
  
###############################################################################
# - S6 - Planned Features --------------------------------------------------- #
###############################################################################
  
  The following features may or may not ever make it into Debreate. If a Target
  Release is specified then it is probably in the works & chances are good that
  it will be available in the future.
  
    Description                                                  Target Release
  ‣ use XML format for saved projects ................................ none yet
  ‣ editiable fields in "Dependencies" & "Files" sections ............ none yet
  ‣ option to create manual pages (man pages) ........................ none yet
  