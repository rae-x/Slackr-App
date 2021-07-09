"""
Contains user_permission_change function and its HTTP route
"""

### Builtin/pip Modules ###
from json import dumps
from flask import request, Blueprint

# pylint: disable=multiple-statements
### Package Modules ###
from error import InputError, AccessError
from data_store import database

### Permission Constants ###
PERMISSION_OWNER = 1
PERMISSION_MEMBER = 2

### Page Blueprint ###
ADMIN_USER_PAGE = Blueprint("admin_user_page", __name__)

### Routes ###

@ADMIN_USER_PAGE.route("/admin/userpermission/change", methods=["POST"])
def route_admin_user_permission_change():
    """
    The HTTP route for user_permission_change
    """
    payload = request.get_json()
    token = payload.get("token")
    user_id = payload.get("u_id")
    permission_id = payload.get("permission_id")

    return dumps(admin_user_permission_change(token, user_id, permission_id))

@ADMIN_USER_PAGE.route('/admin/user/remove', methods=['DELETE'])
def route_admin_user_remove():
    '''
    HTTP route for user/remove
    '''
    payload = request.get_json()
    token = payload.get('token')
    user_id = payload.get('u_id')

    return dumps(admin_user_remove(token, user_id))

### Functions ###

def admin_user_permission_change(token, user_id, permission_id):
    """
    Changes the global permission of a user to either member or owner.
    This can only be evoked by existing owners of the workspace.
    """

    if not isinstance(token, str) or not isinstance(user_id, int) \
    or not isinstance(permission_id, int):
        raise InputError(description="Input error: invalid arguments")

    if permission_id not in (PERMISSION_OWNER, PERMISSION_MEMBER):
        raise InputError(description="Input error: invalid permission type")

    authed_user = database.get_authed_user(token)

    if not authed_user.is_owner():
        raise AccessError(description="Access error: the user making the request is not an owner")

    target_user = database.get_user(user_id)

    if permission_id == PERMISSION_OWNER: database.add_owner(target_user)
    if permission_id == PERMISSION_MEMBER: database.remove_owner(target_user)

    database.update()

    return {}

def admin_user_remove(token, user_id):
    '''
    Removes a user from the slackr

    Arguments:
        token (string)          - Token of the user doing the removing
        user_id (int)           - ID of the user being removed

    Exceptions:
        InputError               - When the user_id given does not exist
        AccessError              - When the authorised user is not an owner of the slackr

    Return Value:
        Returns {} on success

    '''

    if not database.get_authed_user(token):
        raise AccessError(description='Unauthroised User')

    # Raises input error if user_id is invalid
    database.get_user(user_id)

    if database.active_tokens[token] not in database.slackr_owner_ids:
        raise AccessError(description='User must be an owner of the slackr to remove another user')

    database.remove_user(user_id)
    database.update()

    return {}
