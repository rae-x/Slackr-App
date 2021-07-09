'''
channels.py

Contains functions with channels/routes, including:
- channels/create
- channels/listall
- channels/list

'''

### Builtin/pip Modules ###
from json import dumps
from flask import request, Blueprint

### Package Modules ###
from error import AccessError, InputError
from data_store import database
from channel_definition import Channel

### Page Blueprint ###
CHANNELS_PAGE = Blueprint("channels_page", __name__)

### Routes ###

@CHANNELS_PAGE.route("/channels/list", methods=['GET'])
def route_channels_list():
    '''
    Calls function to GET a list of all channels the user is part of
    '''
    token = request.args.get('token')

    return dumps(channels_list(token))

@CHANNELS_PAGE.route('/channels/listall', methods=['GET'])
def route_channels_listall():
    '''
    Calls function to GET a list of all channels
    '''
    token = request.args.get('token')

    return dumps(channels_listall(token))

@CHANNELS_PAGE.route('/channels/create', methods=['POST'])
def route_channels_create():
    '''
    Calls function to create a new channel with POST request contents
    '''
    payload = request.get_json()
    token = payload.get('token')
    name = payload.get('name')
    is_public = payload.get('is_public')

    return dumps(channels_create(token, name, is_public))

### Functions ###

def channels_list(token):
    '''
    Returns a list of channels that the authorised user is in

    Arguments:
        token (string)    - Token of the authorised user

    Return Value:
        Returns a list of channels the authorised user is in on success
    '''
    user = database.get_authed_user(token)

    channels = []

    for channel in database.channels:
        if channel.has_member(user):
            new = {'channel_id': channel.channel_id,
                   'name': channel.name}
            channels.append(new)

    return {'channels': channels}

def channels_listall(token):
    '''
    Returns a list of all channels in the database.

    Arguments:
        token (string)    - Token of the authorised user

    Return Value:
        Returns a list of all the channels on success
    '''
    user = database.get_authed_user(token)

    channels = []

    # Iterates through all channels and adds dictionaries with their details
    for channel in database.channels:
        entry = {'channel_id': channel.channel_id,
                 'name': channel.name}
        channels.append(entry)

    return {'channels': channels}

def channels_create(token, name, is_public):
    '''
    Creates a new channel

    Arguments:
        token (string)    - Token of the authorised user
        name (string)     - Name of the channel
        is_public         - Public status of the channel (true = public, false = private)

    Exceptions:
        InputError  - Occurs when the name is more than 20 characters long

    Return Value:
        Returns the channel id of the created channel on success
    '''
    user = database.get_authed_user(token)

    # Check the name is not more than 20 characters long
    if len(name) > 20:
        raise InputError('Name is more than 20 characters long')

    # Create a new channel and add it to the DB
    new_channel = Channel(name, is_public)

    # Make the user a member and owner
    new_channel.add_owner(user)
    new_channel.add_member(user)
    database.channels.append(new_channel)

    # Update the pickle file
    database.update()

    return {'channel_id': new_channel.channel_id}
