#!/bin/sh

if test $# != 2 ; then
    echo No input files given 1>&2
    exit 1
fi

awk 'BEGIN{FS = " "} { if ($1 ~ /^[A-Za-z]/) {print $1}}' $1 | sort | tr '\n' ';'  > $2