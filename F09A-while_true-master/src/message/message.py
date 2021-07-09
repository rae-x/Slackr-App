'''
messages.py

Contains all functions which involve
sending, editing, reacting, removing and pinning messages in a channel
'''

### Builtin/pip Modules ###
from json import dumps
from time import time
from random import choice
from flask import request, Blueprint

### Package Modules ###
from error import AccessError, InputError
from data_store import database
from message_definition import Message

### Page Blueprint ###
MESSAGE_PAGE = Blueprint('message_page', __name__)

### Routes ###

@MESSAGE_PAGE.route('/message/send', methods=['POST'])
def route_message_send():
    '''
    Calls function to send a message with POST request contents
    '''
    payload = request.get_json()
    token = payload.get('token')
    channel_id = int(payload.get('channel_id'))
    message = payload.get('message')

    return dumps(message_send(token, channel_id, message))

@MESSAGE_PAGE.route('/message/react', methods=['POST'])
def route_message_react():
    '''
    Calls function to record a react to a message
    '''
    payload = request.get_json()
    token = payload.get('token')
    message_id = payload.get('message_id')
    react_id = payload.get('react_id')

    return dumps(message_react(token, message_id, react_id))

@MESSAGE_PAGE.route('/message/unreact', methods=['POST'])
def route_message_unreact():
    '''
    Calls function to record an unreact to a message
    '''
    payload = request.get_json()
    token = payload.get('token')
    message_id = payload.get('message_id')
    react_id = payload.get('react_id')

    return dumps(message_unreact(token, message_id, react_id))

@MESSAGE_PAGE.route('/message/pin', methods=['POST'])
def route_message_pin():
    '''
    Calls a function to record a pin to a message
    '''
    payload = request.get_json()
    token = payload.get('token')
    message_id = payload.get('message_id')

    return dumps(message_pin(token, message_id))

@MESSAGE_PAGE.route('/message/unpin', methods=['POST'])
def route_message_unpin():
    '''
    Calls a function to record a message being unpinned
    '''
    payload = request.get_json()
    token = payload.get('token')
    message_id = payload.get('message_id')

    return dumps(message_unpin(token, message_id))

@MESSAGE_PAGE.route('/message/edit', methods=['PUT'])
def route_message_edit():
    '''
    Calls function to record an edit to a message.
    '''
    payload = request.get_json()
    token = payload.get('token')
    message_id = payload.get('message_id')
    message = payload.get('message')

    return dumps(message_edit(token, message_id, message))

@MESSAGE_PAGE.route('/message/remove', methods=['DELETE'])
def route_message_remove():
    '''
    Calls a function to remove a message.
    '''
    payload = request.get_json()
    token = payload.get('token')
    message_id = payload.get('message_id')

    return dumps(message_remove(token, message_id))

@MESSAGE_PAGE.route('/message/sendlater', methods=['POST'])
def route_message_sendlater():
    '''
    Calls function to send a message with POST request contents at a given time
    '''
    payload = request.get_json()
    token = payload.get('token')
    channel_id = int(payload.get('channel_id'))
    message = payload.get('message')
    send_time = payload.get('time_sent')

    return dumps(message_sendlater(token, channel_id, message, send_time))

### Functions ###

def message_send(token, channel_id, message):
    '''
    Sends a message to a channel

    Arguments:
        token (string)          - Token of the user sending the message
        channel_id (int)        - ID of the channel to send the message to
        message (string)        - text to send

    Exceptions:
        InputError               - When the message is more than 1000 characters long
        AccessError              - When the user is not in the channel they are posting to

    Return Value:
        Returns {'message_id' : ID of new message } on success

    '''
    user = database.get_authed_user(token)

    # Check the message is not more than 1000 characters long
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters long')

    channel = database.get_channel(channel_id)

    if not channel.has_member(user):
        raise AccessError(description='User is not in the channel they are posting to')

    # Send the message to the channel
    time_now = int(time())
    sent_by = user.user_id
    new_message = Message(sent_by, channel.channel_id, message, time_now)
    database.messages.append(new_message)

    play_hangman(channel_id, message, time_now + 1)

    # Update pickle file
    database.update()
    return {'message_id': new_message.message_id}

def message_react(token, message_id, react_id):
    '''
    Records a react to a message

    Arguments:
        token (string)          - Token of the user sending the message
        message_id (int)        - ID of the message being reacted to
        react_id (int)          - type of reaction

    Exceptions:
        InputError               - When the React ID is invalid
                                 - When the message id given does not exist
                                 - When the user has already reacted to the message
        AccessError              - When the user is not in the channel they are reacting to

    Return Value:
        Returns {} on success

    '''

    user = database.get_authed_user(token)

    # Checks that react_id is a valid ID
    if react_id != 1:
        raise InputError(description='React ID is invalid')

    # Checks that the message_id is a valid message
    message = database.get_message(message_id)
    if not message:
        raise InputError(description='Message ID does not exist')

    # Checks that the user has not reacted to the message
    if react_id in message.reacts and user.user_id in message.reacts[react_id]:
        raise InputError(description='You have already reacted to this message')

    # Checks that the user is in the channel
    channel = database.get_channel(message.channel)
    if not channel.has_member(user):
        raise AccessError(description='User is not in the channel they are reacting to')

    # Update the message with the react
    if react_id in message.reacts:
        message.reacts[react_id].append(user.user_id)
    else:
        message.reacts[react_id] = [user.user_id]

    # Update pickle file
    database.update()
    return {}

def message_unreact(token, message_id, react_id):
    '''
    Records an unreact to a message

    Arguments:
        token (string)          - Token of the user sending the message
        message_id (int)        - ID of the message being unreacted to
        react_id (int)          - type of reaction

    Exceptions:
        InputError               - When the React ID is invalid
                                 - When the message id given does not exist
                                 - When the message does not contain a react with the given ID
                                 - When the user tries to remove a react they have not made
        AccessError              - When the user is not in the channel they are unreacting to

    Return Value:
        Returns {} on success

    '''
    user = database.get_authed_user(token)

    # Checks that react_id is a valid ID
    if react_id != 1:
        raise InputError(description='React ID is invalid')

    # Checks that the message_id is a valid message
    message = database.get_message(message_id)
    if not message:
        raise InputError(description='Message ID does not exist')

    # Checks that the user is in the channel
    channel = database.get_channel(message.channel)
    if not channel.has_member(user):
        raise AccessError(description='User is not in the channel they are un-reacting to')

    # Checks that the react_id is in the message reacts
    if react_id not in message.reacts:
        raise InputError(description='Message does not contain a react with that ID')

    # Checks that the user has reacted on the message before
    if react_id in message.reacts and user.user_id not in message.reacts[react_id]:
        raise InputError(description='You cannot remove a react you did not make')

    # Update the message with the react
    message.reacts[react_id].remove(user.user_id)
    if not message.reacts[react_id]:
        del message.reacts[react_id]

    # Update pickle file
    database.update()
    return {}

def message_pin(token, message_id):
    '''
    Records a message being pinned

    Arguments:
        token (string)          - Token of the user sending the message
        message_id (int)        - ID of the message being pinned

    Exceptions:
        InputError               - When the message id given does not exist
                                 - When the message is already pinned
        AccessError              - When the user is not in the channel they are pinning on

    Return Value:
        Returns {} on success

    '''
    user = database.get_authed_user(token)

    # Checks that the message_id is a valid message
    message = database.get_message(message_id)
    if not message:
        raise InputError(description='Message ID does not exist')

    # Checks that the user is in the channel
    channel = database.get_channel(message.channel)
    if not channel.has_member(user):
        raise AccessError(description='User is not in the channel they are pinning on')

    if message.pinned:
        raise InputError(description='Message is already pinned')

    # Update the message with the pin
    message.pinned = True

    # Update pickle file
    database.update()
    return {}

def message_unpin(token, message_id):
    '''
    Records a message being unpinned

    Arguments:
        token (string)          - Token of the user sending the message
        message_id (int)        - ID of the message being unpinned

    Exceptions:
        InputError               - When the message id given does not exist
                                 - When the message is not pinned
        AccessError              - When the user is not in the channel they are unpinning on

    Return Value:
        Returns {} on success

    '''
    user = database.get_authed_user(token)

    # Checks that the message_id is a valid message
    message = database.get_message(message_id)
    if not message:
        raise InputError(description='Message ID does not exist')

    # Checks that the user is in the channel
    channel = database.get_channel(message.channel)
    if not channel.has_member(user):
        raise AccessError(description='User is not in the channel they are unpinning on')

    if not message.pinned:
        raise InputError(description='Message is already unpinned')

    # Update the message with the unpin
    message.pinned = False

    # Update pickle file
    database.update()
    return {}

def message_edit(token, message_id, updated_content):
    '''
    Edits a message by overwriting the current content with given content.

    Arguments:
        token (string)           - Token of the user sending the message
        message_id (int)         - ID of the message being edited
        updated_content (string) - updated content of the message to be posted

    Exceptions:
        InputError               - When the message id given does not exist
                                 - When the message is more than 1000 character long
        AccessError              - When the user is did not send the message they are trying to edit
                                 - When the user is not a channel/slackr owner

    Return Value:
        Returns {} on success

    '''
    user = database.get_authed_user(token)

    # Checks that the message_id is a valid message
    message = database.get_message(message_id)
    if not message:
        raise InputError(description='Message ID does not exist')

    channel = database.get_channel(message.channel)

    # Checks the message was sent by the user editing it
    # Checks that the user is an owner of the channel/slackr
    if message.sent_by != database.active_tokens[token] and not channel.has_owner(user) and not user.is_owner():
        raise AccessError(description='User did not send the message they are trying to edit')

    # Checks the new content is not more than 1000 characters long
    if len(updated_content) > 1000:
        raise InputError(description='Message is more than 1000 characters long')

    # Updates the message with the new content
    if updated_content == '':
        message_remove(token, message_id)
    else:
        message.content = updated_content

    # Update pickle file
    database.update()
    return {}

def message_remove(token, message_id):
    '''
    Removes a message with the given ID.

    Arguments:
        token (string)          - Token of the user sending the message
        message_id (int)        - ID of the message being removed

    Exceptions:
        InputError               - When the message id given does not exist
        AccessError              - When the user did not send the message being removed
                                 - When the user is not a channel/slackr owner

    Return Value:
        Returns {} on success

    '''
    user = database.get_authed_user(token)

    # Checks that the message_id is a valid message
    message = database.get_message(message_id)
    if not message:
        raise InputError(description='Message ID does not exist')

    channel = database.get_channel(message.channel)

    # Checks the message was sent by the user removing it
    # Checks that the user is an owner of the channel/slackr
    if message.sent_by != database.active_tokens[token] and not channel.has_owner(user) and not user.is_owner():
        raise AccessError(description='User did not send the message they are trying to remove')

    # Removes the message
    database.messages.remove(message)

    # Update pickle file
    database.update()
    return {}

def message_sendlater(token, channel_id, message, send_time):
    '''
    Saves a message to be sent at a given time to a channel

    Arguments:
        token (string)          - Token of the user sending the message
        channel_id (int)        - ID of the channel to send the message to
        message (string)        - text to send
        send_time (int)         - time to send the message

    Exceptions:
        InputError               - When the message is more than 1000 characters long
                                 - When the time to send is in the past
        AccessError              - When the user is not in the channel they are posting to

    Return Value:
        Returns {'message_id' : ID of new message } on success

    '''
    user = database.get_authed_user(token)

    # Check the message is not more than 1000 characters long
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters long')

    channel = database.get_channel(channel_id)
    if not channel:
        raise InputError(description='Channel ID does not exist')

    # Checks the user is in the channel
    if not channel.has_member(user):
        raise AccessError(description='User is not in the channel they are posting to')

    time_now = int(time())

    # Checks the time sent is not in the past
    if send_time < time_now:
        raise InputError(description='Time sent is a time in the past')

    sent_by = database.active_tokens[token]

    new_message = Message(sent_by, channel.channel_id, message, send_time)
    # If the message send time is after the current time,
    # then channel/messages and /search won't list it

    # Send the message to the channel
    database.messages.append(new_message)

    # Update pickle file
    database.update()
    return {'message_id': new_message.message_id}

HANGMAN_ID = 0

def play_hangman(channel_id, message, time_now):

    channel = database.get_channel(channel_id)
    if message == '/hangman':
        # Start a game of hangman
        # print('We are going to play a game of hangman')
        channel.hangman_word = get_hangman_word()
        channel.hangman_active = True
        channel.hangman_guesses_correct = set()
        channel.hangman_guesses_incorrect = set()

        hangman_message = Message(HANGMAN_ID, channel_id, f'{channel.hangman_word}&&', time_now)
        database.messages.append(hangman_message)

    elif message.startswith('/guess'):
        if not channel.hangman_active:
            hangman_message = Message(HANGMAN_ID, channel_id, "Please start a game first, with /hangman", time_now)
            database.messages.append(hangman_message)
            return

        # Make a guess
        guess = message.lstrip('/guess')

        guess = guess[1:].lower()
        if not guess.isalpha():
            return
        
        if len(guess) > 1:
            if guess == channel.hangman_word:
                channel.hangman_guesses_correct = channel.hangman_guesses_correct | set(guess)
            else:
                channel.hangman_guesses_incorrect.add(str(len(channel.hangman_guesses_incorrect)))
        else:
            if guess in channel.hangman_word:
                # Correct guess
                channel.hangman_guesses_correct.add(guess)
            else:
                channel.hangman_guesses_incorrect.add(guess)

        correct_guess_format = ','.join(list(channel.hangman_guesses_correct))
        incorrect_guess_format = ','.join(list(channel.hangman_guesses_incorrect))
        hangman_message = Message(HANGMAN_ID, channel_id, f'{channel.hangman_word}&{correct_guess_format}&{incorrect_guess_format}', time_now)
        database.messages.append(hangman_message)

        # Check if the hangman is solved
        solved = True
        for letter in channel.hangman_word:
            if not letter in channel.hangman_guesses_correct:
                solved = False
                break

        dead = len(channel.hangman_guesses_incorrect) >= 6
        if solved or dead:
            string = 'Hangman solved!'
            if dead: string = 'Hangman dead! The word was "' + channel.hangman_word + '"'
            hangman_message = Message(HANGMAN_ID, channel_id, string, time_now + 1)
            database.messages.append(hangman_message)
            channel.hangman_active = False

    database.update()


def get_hangman_word():

    words = open('/usr/share/dict/british-english').readlines()
    words = map(lambda word: word.strip('\n'), words)
    words = list(filter(lambda word: word.isalpha() and len(word) <= 9, words))
    word = choice(words)

    return word
