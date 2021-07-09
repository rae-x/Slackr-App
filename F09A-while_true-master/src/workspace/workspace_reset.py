"""
Contains workspace_reset function and its HTTP route
"""

### Builtin/pip Modules ###
from json import dumps
from flask import Blueprint

### Package Modules ###
from data_store import database

### Page Blueprint ###
WORKSPACE_RESET_PAGE = Blueprint("workspace_reset", __name__)

### Routes ###

@WORKSPACE_RESET_PAGE.route("/workspace/reset", methods=["POST"])
def route_workspace_reset():
    """
    HTTP route for workspace_reset
    """
    return dumps(workspace_reset())

### Functions ###

def workspace_reset():
    """
    Clears all data in the workspace
    """
    database.reset()
    return {}
