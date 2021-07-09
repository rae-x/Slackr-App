#!/bin/sh

CURDIR=$(pwd)

# Set the python path for the individual modules
PYTHONPATH="$CURDIR/src:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/error:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/auth:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/channel:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/channels:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/message:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/user:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/users:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/search:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/standup:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/admin:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/workspace:${PYTHONPATH}"
PYTHONPATH="$CURDIR/src/definitions:${PYTHONPATH}"

# Make the visible on the environment level
export PYTHONPATH

# Run pylint or pylint3 depending on what you have
if [ -z $(which pylint3) ]; then
    if [ "$#" -gt 0 ]; then
        # Run pylint with the arguments passed in if any
        pylint "$@"
    else
        # Run pylint on src/* if no arguments passed in
        pylint src/*
    fi
else
    if [ "$#" -gt 0 ]; then
        # Run pylint with the arguments passed in if any
        pylint3 "$@"
    else
        # Run pylint on src/* if no arguments passed in
        pylint3 src/*
    fi
fi

# Remove the variable on the environment level
unset PYTHONPATH
