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

# Run server.py with a port if supplied, else run without
# a chosen port
if [ -n $1 ]; then
    python3 src/server.py $1
else
    python3 src/server.py
fi

# Remove the variable on the environment level
unset PYTHONPATH
