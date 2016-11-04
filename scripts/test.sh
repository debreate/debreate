#!/usr/bin/env bash

find ./ -type f -name "*\.pyc" -print -delete

./init.py $@

echo "Debreate exit code: $?"

find ./ -type f -name "*\.pyc" -delete
