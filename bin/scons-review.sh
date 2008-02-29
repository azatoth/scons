#!/bin/sh

if test "X$1" = "X-m"; then
    svn diff --diff-cmd diff -x -c $* | alpine scons-dev
else
    svn diff --diff-cmd diff -x -c $*
fi

# OLD CODE FOR USE WITH AEGIS
#
#if test $# -ne 1; then
#    echo "Usage:  scons-review change#" >&2
#    exit 1
#fi
#if test "X$AEGIS_PROJECT" = "X"; then
#    echo "scons-review:  AEGIS_PROJECT is not set" >&2
#    exit 1
#fi
#DIR=`aegis -cd -dd $*`
#if test "X${DIR}" = "X"; then
#    echo "scons-review:  No Aegis directory for '$*'" >&2
#    exit 1
#fi
#(cd ${DIR} && find * -name '*,D' | sort | xargs cat) | pine scons-dev
