
cmake_minimum_required(VERSION 3.5)
project(Debreate NONE)

find_package(PythonInterp 2.7 REQUIRED)
#include(FindPythonInterp)
#find_package(Gettext)
include(FindGettext)

set(DATA_ROOT "share")
set(DATA_DIR "${DATA_ROOT}/debreate")
set(APPS_DIR "${DATA_ROOT}/applications")
set(BITMAPS_DIR "${DATA_ROOT}/bitmaps")

# Make Python interpreter alterable
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
    DIRECTORY dbr f_export globals input output startup system ui wiz_bin wiz_src
    DESTINATION ${DATA_DIR}
    FILES_MATCHING
    PATTERN *.py
)

# FIXME: Not all docs should be installed
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
        FILES bitmaps/icon/64/logo.png
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

# Write the Debreate executable
file(
    WRITE "${CMAKE_BINARY_DIR}/bin/debreate"
    "#!/bin/sh"
    "\n\n${CMAKE_INSTALL_PREFIX}/${DATA_DIR}/init.py $@"
)

install(
    FILES "${CMAKE_BINARY_DIR}/bin/debreate"
    DESTINATION bin
    PERMISSIONS ${EXECUTABLE_PERMISSIONS}
)

# Write the "INSTALLED" file
set(FILE_installed "${CMAKE_BINARY_DIR}/data/INSTALLED")

file(
    WRITE "${FILE_installed}"
    "prefix=${CMAKE_INSTALL_PREFIX}"
)

install(
    FILES "${FILE_installed}"
    DESTINATION "${DATA_DIR}"
)
