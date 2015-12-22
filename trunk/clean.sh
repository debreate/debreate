#!/bin/sh

# A script for cleaning up the workspace

ROOTDIR=`dirname $0`
if [ -z "${FULL}" ]; then
	FULL=0
fi

find "${ROOTDIR}" -type f \( -name "*.pyc" \) -exec rm -v {} +;

if [ "${FULL}" -gt "0" ]; then
	find "${ROOTDIR}" -type f \( -name "*.log" -o -name "*.status" \)  -exec rm -v {} +;
	find "${ROOTDIR}" -type d \( -name "*.cache" \) -exec rm -vr {} +;
fi
