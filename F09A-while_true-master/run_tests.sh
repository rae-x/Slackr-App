#!/bin/sh

echo "Make sure the server is running before running this"
read -p "Press the ENTER key to continue... " dummy

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

# Run pytest with coverage
if [ "$#" -gt 0 ]; then
    # Run pytest with the arguments passed in if any
    python3-coverage run --source=. -m pytest "$@"
else
    # Run pytest on src/* if no arguments passed in
    python3-coverage run --source=. -m pytest src/*
fi

# Run coverage report and generate the results in html form
python3-coverage report
python3-coverage html

echo ""
echo "python-coverage html has been run, check the htmlcov folder."

# Remove the variable on the environment level
unset PYTHONPATH
