#!/usr/bin/env bash

# helper script to scan source & update Gettext translatable strings

dir_scripts="$(dirname $0)"
cd "${dir_scripts}/.."
dir_root="$(pwd)"

file_pot="${dir_root}/locale/debreate.pot"


# parse version info (don't import file directly because of whitespace in values)
echo -e "\nParsing app information ..."
appinfo=$(cat "INFO")
appname=$(echo "${appinfo}" | grep "^NAME=" | sed 's/^NAME=//')
appver=$(echo "${appinfo}" | grep "^VERSION=" | sed 's/^VERSION=//')
author=$(echo "${appinfo}" | grep "^AUTHOR=" | sed 's/^AUTHOR=//')
email=$(echo "${appinfo}" | grep "^EMAIL=" | sed 's/^EMAIL=//')


# parse source files
echo -e "\nGathering list of files to check for translatable strings ..."
source_list=("command_line.py" "init.py" "main.py")
for subdir in dbr globals f_export fields fileio input startup system ui wiz wizbin; do
	source_list+=($(find "${subdir}" -type f -name "*.py"))
done


# update translatable strings
echo -e "\nUpdating locale template ..."

# check for xgettext command
which xgettext > /dev/null 2>&1
res=$?
if [ ${res} -ne 0 ]; then
	echo -e "\nERROR: xgettext command not found"
	# FIXME: correct errno
	exit 1
fi

xgettext \
	--language=Python \
	--keyword \
	--keyword=GT \
	--indent \
	--no-wrap \
	--sort-output \
	--no-location \
	--copyright-holder="${author}" \
	--package-name="${appname}" \
	--package-version="${appver}" \
	--msgid-bugs-address="${email}" \
	--default-domain="$(echo "${appname}" | tr "[:upper:]" "[:lower:]")" \
	--output="${file_pot}" \
	${source_list[@]}

# update header
sed -i \
	-e 's/^# SOME DESCRIPTIVE TITLE\.$/# Debreate - Debian Package Builder/' \
	-e "s/^# Copyright (C) YEAR/# Copyright © $(date +%Y)/" \
	"${file_pot}"

lcount=$(cat "${file_pot}" | wc -l)
pre="$(cat "${file_pot}" | head -n5)"
post="$(cat "${file_pot}" | tail -n$(expr ${lcount} - 5))"

# notes to add to header
notes='# NOTES:
#   If "%s" or "{}" is in the msgid, be sure to put it in
#   the msgstr or parts of Debreate will not function.
#
#   If you do not wish to translate a line just leave its
#   msgstr blank'

echo "${pre}
${notes}
${post}" > "${file_pot}"


echo -e "\nUpdating locale translations ..."

which msgmerge > /dev/null 2>&1
res=$?
if [ ${res} -ne 0 ]; then
	echo -e "\nERROR: msgmerge command not found"
	# FIXME: correct errno
	exit 1
fi

language_files=($(find "locale/" -type f -name "*.po"))

for file_po in ${language_files[@]}; do
	echo "Updating: ${file_po} ..."
	msgmerge \
		--update \
		--indent \
		--sort-output \
		--no-fuzzy-matching \
		--no-location \
		--no-wrap \
		--backup=none \
		--previous \
		"${file_po}" \
		"${file_pot}"
done


# compile .mo files
# FIXME: this should be done at time of build/release
echo -e "\nCompiling locale translations ..."

which msgfmt > /dev/null 2>&1
res=$?
if [ ${res} -ne 0 ]; then
	echo -e "\nERROR: msgfmt command not found"
	# FIXME: correct errno
	exit 1
fi

for file_po in ${language_files[@]}; do
	dir_lang="$(dirname "${file_po}")"
	dir_target="${dir_lang}/LC_MESSAGES"
	lang="$(basename "${dir_lang}")"
	echo "Compiling language ${lang} ..."
	msgfmt \
		--output-file="${dir_target}/debreate.mo" \
		"${file_po}"
done
