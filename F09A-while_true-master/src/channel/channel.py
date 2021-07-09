"""
Contains channel routes and their functions of the following:

    /channel/invite
    /channel/details
    /channel/messages
    /channel/leave
    /channel/join
    /channel/addowner
    /channel/removeowner
"""

### Builtin/pip Modules ###
from json import dumps
from flask import request, Blueprint

### Package Modules ###
from error import AccessError, InputError
from data_store import database

### Page Blueprint ###
CHANNEL_PAGE = Blueprint("channel_page", __name__)

### Routes ###

@CHANNEL_PAGE.route("/channel/invite", methods=["POST"])
def route_channel_invite():
    """
    /channel/invite POST route
    """
    payload = request.get_json()
    token = payload.get("token")
    channel_id = int(payload.get("channel_id"))
    u_id = payload.get("u_id")

    return dumps(channel_invite(token, channel_id, u_id))

@CHANNEL_PAGE.route("/channel/details", methods=["GET"])
def route_channel_details():
    """
    /channel/details GET route
    """
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))

    return dumps(channel_details(token, channel_id))

@CHANNEL_PAGE.route("/channel/messages", methods=["GET"])
def route_channel_messages():
    """
    /channel/messages GET route
    """
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    start = int(request.args.get("start"))

    return dumps(channel_messages(token, channel_id, start))

@CHANNEL_PAGE.route("/channel/leave", methods=["POST"])
def route_channel_leave():
    """
    /channel/leave POST route
    """
    payload = request.get_json()
    token = payload.get("token")
    channel_id = int(payload.get("channel_id"))

    return dumps(channel_leave(token, channel_id))

@CHANNEL_PAGE.route("/channel/join", methods=["POST"])
def route_channel_join():
    """
    /channel/join POST route
    """
    payload = request.get_json()
    token = payload.get("token")
    channel_id = int(payload.get("channel_id"))

    return dumps(channel_join(token, channel_id))

@CHANNEL_PAGE.route("/channel/addowner", methods=["POST"])
def route_channel_addowner():
    """
    /channel/addowner POST route
    """
    payload = request.get_json()
    token = payload.get("token")
    channel_id = int(payload.get("channel_id"))
    u_id = payload.get("u_id")

    return dumps(channel_addowner(token, channel_id, u_id))

@CHANNEL_PAGE.route("/channel/removeowner", methods=["POST"])
def route_channel_removeowner():
    """
    /channel/removeowner POST route
    """
    payload = request.get_json()
    token = payload.get("token")
    channel_id = int(payload.get("channel_id"))
    u_id = payload.get("u_id")

    return dumps(channel_removeowner(token, channel_id, u_id))

### Functions ###

def channel_invite(token, channel_id, u_id):
    """
    Invites a user to a channel

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID
        u_id (int)        - User ID of the user being invited

    Exceptions:
        InputError  - Occurs when the user is already in the channel

        AccessError - Occurs when the authorised user is not in the channel

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)
    target_user = database.get_user(u_id)
    channel = database.get_channel(channel_id)

    # Error checking
    if channel.has_member(target_user):
        raise InputError(description="User is already in the channel")
    if not channel.has_member(authed_user):
        raise AccessError(description="Unauthorised User")

    # Add user to the channel
    channel.add_member(target_user)
    database.update()

    return {}

def channel_details(token, channel_id):
    """
    Provides name, owners and non-owner members of a channel

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID

    Exceptions:
        AccessError - Occurs when the authorised user is not in the channel

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)

    # Get the channel
    channel = database.get_channel(channel_id)

    # Error checking
    if not channel.has_member(authed_user):
        raise AccessError(description="Unauthorised User")

    return channel.json()

def channel_messages(token, channel_id, start):
    """
    Returns up to 50 messages between start and start + 49 inclusive

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID
        start (int)       - int

    Exceptions:
        InputError - Occurs when the start is greater than or equal to the
                     number of messages or less than 0

        AccessError - Occurs when the authorised user is not in the channel

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)
    channel = database.get_channel(channel_id)

    # Error checking
    if not channel.has_member(authed_user):
        raise AccessError(description="Unauthorised User")

    messages = channel.json_messages(authed_user)

    # Error checking
    # Do not raise error if there are no messages and start is 0
    if (start >= len(messages) or start < 0) \
            and not (len(messages) == 0 and start == 0):
        raise InputError(description="Start is not valid")

    # Set end accordingly. If end greater than the length of messages,
    # -1 is set to denote no more messages to load
    end = start + 50
    if end >= len(messages):
        end = -1

    # Slice the messages list to get messages from index of
    # start + 0 ... start + 49 messages inclusive
    messages = messages[start:]
    messages = messages[:50]

    # Store data in payload and return
    payload = {"messages": messages, "start": start, "end": end}
    return payload

def channel_leave(token, channel_id):
    """
    Removes a user from the channel

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID

    Exceptions:
        InputError  - Occurs when the authorised user is an owner

        AccessError - Occurs when the authorised user is not in the channel

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)
    channel = database.get_channel(channel_id)

    # Error checking
    if not channel.has_member(authed_user):
        raise AccessError(description="Unauthorised User")
    if channel.has_owner(authed_user):
        raise InputError(description="Owners cannot leave the channel")

    # Remove user from channel
    channel.remove_member(authed_user)
    database.update()

    return {}

def channel_join(token, channel_id):
    """
    Adds a user to the channel

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID

    Exceptions:
        InputError  - Occurs when the authorised user is already in the channel

        AccessError - Occurs when the authorised user is not a slackr owner and
                      the channel is private

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)
    channel = database.get_channel(channel_id)

    # Error checking
    if not channel.is_public and not authed_user.is_owner():
        raise AccessError(description="Unauthorised User")
    if channel.has_member(authed_user):
        raise InputError(description="User is already in the channel")

    # Add user to the channel
    channel.add_member(authed_user)
    database.update()

    return {}

def channel_addowner(token, channel_id, u_id):
    """
    Makes a user an owner of the channel

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID
        u_id (int)        - User ID of the user being invited

    Exceptions:
        InputError  - Occurs when the user is not in the channel
                    - Occurs when the user is already an owner of the channel

        AccessError - Occurs when the authorised user is not a slackr owner and
                      the not an owner of the channel

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)
    target_user = database.get_user(u_id)
    channel = database.get_channel(channel_id)

    # Error checking
    if not channel.has_member(target_user):
        raise InputError(description="User is not in the channel")
    if not channel.has_owner(authed_user) and not authed_user.is_owner():
        raise AccessError(description="Unauthorised User")
    if channel.has_owner(target_user):
        raise InputError(description="User is already an owner of the channel")

    # Make user an owner
    channel.add_owner(target_user)
    database.update()

    return {}

def channel_removeowner(token, channel_id, u_id):
    """
    Remove a user as an owner of the channel

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID
        u_id (int)        - User ID of the user being invited

    Exceptions:
        InputError  - Occurs when the user is not in the channel
                    - Occurs when the user is not an owner of the channel

        AccessError - Occurs when the authorised user is not a slackr owner and
                      the not an owner of the channel

    Return Value:
        Returns {} on success
    """
    authed_user = database.get_authed_user(token)
    target_user = database.get_user(u_id)
    channel = database.get_channel(channel_id)

    # Error checking
    if not channel.has_member(target_user):
        raise InputError(description="User is not in the channel")
    if not channel.has_owner(authed_user) and not authed_user.is_owner():
        raise AccessError(description="Unauthorised User")
    if not channel.has_owner(target_user):
        raise InputError(description="User is not an owner of the channel")

    # Remove user as an owner
    channel.remove_owner(target_user)
    database.update()

    return {}
