"""
Contains users_all function and its HTTP route
"""

### Builtin/pip Modules ###
from json import dumps
from flask import request, Blueprint

### Package Modules ###
from error import InputError
from data_store import database

### Page Blueprint ###
USERS_ALL_PAGE = Blueprint("users_page", __name__)

### Routes ###

@USERS_ALL_PAGE.route("/users/all", methods=["GET"])
def route_users_all():
    """
    HTTP route for users_all
    """
    token = request.args.get("token")
    return dumps(users_all(token))

### Functions ###

def users_all(token):
    """
    Returns a list of all users in the workspace
    """

    if not isinstance(token, str):
        raise InputError(description="Input error: invalid arguments")

    data = {"users": []}
    users = data["users"]

    if database.get_authed_user(token, error=False):
        for user in database.users:
            users.append({
                "u_id": user.user_id,
                "email": user.email,
                "name_first": user.name_first,
                "name_last": user.name_last,
                "handle_str": user.handle,
                "profile_img_url": user.profile_img_url
            })

    return data
