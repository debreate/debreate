cmake_minimum_required(VERSION 3.5)
project(Debreate NONE)
#include(FindPythonInterp)
#include(FindGettext)

find_package(PythonInterp 2.7 REQUIRED)
find_package(Gettext)

set(DATA_DIR share/debreate)
set(APPS_DIR share/applications)
set(BITMAPS_DIR share/bitmaps)
set(LOCALE_DIR share/locale)

if(PYTHONINTERP_FOUND)
    set(PYTHON_EXE ${PYTHON_EXECUTABLE})
    unset(PYTHON_EXECUTABLE CACHE)
    set(PYTHON_EXECUTABLE ${PYTHON_EXE} CACHE FILEPATH "The Python interpreter")
endif()

option(
    INSTALL_MENU_LAUNCHER
    "Installs a .desktop file for executing Debreate from the system menu"
    ON
)

option(
    CONFIGURE_MIME_TYPES
    "Associates .dbp & .dbpz project files with Debreate"
    ON
)

set(
    EXECUTABLE_PERMISSIONS
    OWNER_READ OWNER_WRITE OWNER_EXECUTE
    GROUP_READ GROUP_EXECUTE
    WORLD_READ WORLD_EXECUTE
)

# Executable script
install(
    FILES init.py
    DESTINATION ${DATA_DIR}
    PERMISSIONS ${EXECUTABLE_PERMISSIONS}
)

install(
    FILES main.py command_line.py
    DESTINATION ${DATA_DIR}
)

install(
    DIRECTORY globals dbr wiz_bin wiz_src
    DESTINATION ${DATA_DIR}
    FILES_MATCHING
    PATTERN *.py
)

install(
    DIRECTORY bitmaps docs templates
    DESTINATION ${DATA_DIR}
)


if(INSTALL_MENU_LAUNCHER)
    install(
        FILES data/debreate.desktop
        DESTINATION ${APPS_DIR}
    )
    install(
        FILES bitmaps/debreate64.png
        DESTINATION ${BITMAPS_DIR}
        RENAME debreate.png
    )
endif()

# Gettext locales
if(GETTEXT_FOUND)
    option(
        INSTALL_LOCALE_FILES
        "Installs Gettext translation files to system locale directory"
        ON
    )
    
    if(INSTALL_LOCALE_FILES)
        install(
            DIRECTORY locale
            DESTINATION share
            FILES_MATCHING
            PATTERN *.mo
        )
    endif()
else()
    message("Gettext not found, can't create locale files")
endif()

if(CONFIGURE_MIME_TYPES)
    message("CONFIGURE_MIME_TYPES:\tON")
else()
    message("CONFIGURE_MIME_TYPES:\tOFF")
endif()

file(
    WRITE "${CMAKE_BINARY_DIR}/bin/debreate"
    "#!/bin/bash -e"
    "\n\n${CMAKE_INSTALL_PREFIX}/${DATA_DIR}/init.py $@"
)

install(
    FILES "${CMAKE_BINARY_DIR}/bin/debreate"
    DESTINATION bin
    PERMISSIONS ${EXECUTABLE_PERMISSIONS}
)
