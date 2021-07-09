'''
implementations for standup
'''

### Builtin/pip Modules ###
from json import dumps
from datetime import timezone, datetime, timedelta
from threading import Timer
from flask import request, Blueprint

### Package Modules ###
from error import InputError, AccessError
from message import message_send
from data_store import database

### Page Blueprint ###
STANDUP_PAGE = Blueprint("standup_page", __name__)

### Routes ###

@STANDUP_PAGE.route("/standup/start", methods=['POST'])
def route_standup_start():
    '''
    route for standup_start
    '''
    payload = request.get_json()
    token = payload.get('token')
    channel_id = int(payload.get('channel_id'))
    length = payload.get('length')
    return dumps(standup_start(token, channel_id, length))

@STANDUP_PAGE.route("/standup/active", methods=['GET'])
def route_standup_active():
    '''
    route for standup_active
    '''
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    return dumps(standup_active(token, channel_id))

@STANDUP_PAGE.route("/standup/send", methods=['POST'])
def route_standup_send():
    '''
    route for standup_send
    '''
    payload = request.get_json()
    token = payload.get('token')
    channel_id = int(payload.get('channel_id'))
    message = payload.get('message')
    return dumps(standup_send(token, channel_id, message))

### Functions ###

def standup_start(token, channel_id, length):
    '''
    Starts the standup given seconds in length.

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID
        length (int)      - Length of the standup in seconds

    Exceptions:
        InputError  - Occurs when the channel id is not a valid channel
                    - Occurs when a standup is already active in the channel
        AccessError - Occurs when the user is not in the channel

    Return Value:
        Returns {time_finish} on success
    '''
    user = database.get_authed_user(token)
    channel = database.get_channel(channel_id)

    if not channel.has_member(user):
        raise AccessError(description="User not in the channel")

    current = datetime.utcnow()
    time_finish = current + timedelta(seconds=length)
    time_finish = time_finish.replace(tzinfo=timezone.utc).timestamp()

    if channel.is_active is True:
        raise InputError(description="Channel already active")

    channel.time_finish = time_finish
    channel.is_active = True

    database.update()

    timer = Timer(length, create_standup_message, [token, channel])
    timer.start()

    return {"time_finish": time_finish}

def standup_active(token, channel_id):
    '''
    Return whether a standup is active in the channel or not

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID

    Exceptions:
        InputError  - Occurs when the channel id is not a valid channel
        AccessError - Occurs when the user is not in the channel

    Return Value:
        Returns {is_active, time_finish} on success

    '''
    user = database.get_authed_user(token)
    channel = database.get_channel(channel_id)

    if not channel.has_member(user):
        raise AccessError(description="User not in the channel")

    current = datetime.utcnow()
    current = float(current.replace(tzinfo=timezone.utc).timestamp())

    is_active = False
    time_finish = None

    # Set is_active and time_finish accordingly
    if channel.is_active is False:
        is_active = False
        time_finish = None
    elif channel.time_finish <= current:
        # Standup has finished, update the channel's fields
        channel.is_active = False
        channel.time_finish = None
        channel.buffer = []
    else:
        is_active = True
        time_finish = channel.time_finish

    database.update()

    return {"is_active": is_active, "time_finish": time_finish}

def standup_send(token, channel_id, message):
    '''
    Save the messages during the standup to the buffer

    Arguments:
        token (string)    - Token of the authorised user
        channel_id (int)  - Channel ID
        message (str)     - Messages saved during standup

    Exceptions:
        InputError  - Occurs when the channel id is not a valid channel
                    - Occurs when message is more than 1000 characters
                    - Occurs when an active standup is not currently running
        AccessError - Occurs when the user is not in the channel

    Return Value:
        Returns {} on success
    '''
    user = database.get_authed_user(token)
    channel = database.get_channel(channel_id)
    handle = user.handle

    if not channel.has_member(user):
        raise AccessError(description="User not in the channel")

    if len(message) > 1000:
        raise InputError(description="Message is greater than 1000 characters")

    if channel.is_active is False:
        raise InputError(description="An active standup is not currently running in this channel")

    new_message = handle + ': ' + message + '\n'
    channel.buffer.append(new_message)

    database.update()

    return {}

### Helper Functions ###

def create_standup_message(token, channel):
    '''
    Create the standup message from the buffered messages
    '''
    message = "".join(channel.buffer).rstrip()
    message_send(token, channel.channel_id, message)
