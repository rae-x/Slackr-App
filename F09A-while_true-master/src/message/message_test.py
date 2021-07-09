'''
message_test.py

Integration tests for message functions:
- message_send
- message_edit
- message_remove
- message_react
- message_unreact
- message_pin
- message_unpin
- message_sendlater
'''

# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable

# Builtin modules
from time import time, sleep
import pytest
# Core Package Modules
from error import InputError, AccessError
# Functions for setup
from auth import auth_register, auth_logout, auth_login
from channels import channels_create
from channel import channel_removeowner, channel_messages
from search import search
from workspace_reset import workspace_reset
# Functions to be tested
from message import message_send, message_edit, message_remove, message_sendlater
from message import message_react, message_unreact, message_pin, message_unpin
from admin_user import admin_user_permission_change

@pytest.fixture(autouse=True)
def call_workspace_reset():
    ''' Automatic fixture to reset state between tests '''
    workspace_reset()

@pytest.fixture
def setup_channel():
    '''
    Sets up the data store to be used and clears it
    '''
    # Registers a new user, creates a new channel and adds them to that channel
    # Assumption - user is not automatically added to a channel when the channel is created
    register_results = auth_register('z5169779@ad.unsw.edu.au', 'abc123', 'Joe', 'Bloggs')
    token = register_results['token']
    u_id = register_results['u_id']

    new_channel = channels_create(token, 'My First Channel', True)

    return token, new_channel['channel_id'], u_id

### Testing message_send function

def test_valid_message_send(setup_channel):
    '''
    Testing a valid message
    '''
    token, channel_id, _ = setup_channel

    message_results = message_send(token, channel_id, 'Hey everyone')

    # Testing that the new message has a message ID
    assert message_results['message_id'] == 1

    # Testing that searching for this message returns the message
    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['message_id'] == 1
    assert searched_message['message'] == 'Hey everyone'

def test_long_message_send(setup_channel):
    '''
    Testing a message that is longer than 1000 characters
    '''

    token, channel_id, u_id = setup_channel

    with pytest.raises(InputError) as _:
        long_message = 'x' * 1001
        message_id = message_send(token, channel_id, long_message)

def test_unjoined_channel_message_send(setup_channel):
    '''
    Testing sending message when the user hasn't joined the channel
    '''
    token, channel_id, u_id = setup_channel

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    unjoined_channel_id = channels_create(token, 'A Second Channel', False)['channel_id']
    auth_logout(token)

    token = auth_login('z5169779@ad.unsw.edu.au', 'abc123')['token']

    with pytest.raises(AccessError) as _:
        message_id = message_send(token, unjoined_channel_id, 'Hey everyone')

def test_invalid_token_message_send(setup_channel):
    '''
    Testing sending a message with an invalid token
    '''
    fake_token, channel_id = '', setup_channel[1]

    with pytest.raises(AccessError) as _:
        message_id = message_send(fake_token, channel_id, 'Hey everyone')

def test_invalid_id_message_send(setup_channel):
    '''
    Testing sending a message with an invalid channel ID
    '''

    token, fake_channel_id = setup_channel[0], 'fakeId'

    with pytest.raises(InputError) as _:
        message_id = message_send(token, fake_channel_id, 'Hey everyone')

### Testing message_edit function

@pytest.fixture
def setup_message(setup_channel):
    '''
    Registers a new user, creates a new channel and adds
    the user to the channel using setup_channel
    Sends a message to the channel
    '''
    token, channel_id, u_id = setup_channel

    new_message = message_send(token, channel_id, 'Hey everyone')
    return token, new_message['message_id'], u_id, channel_id

def test_valid_message_edit(setup_message):
    '''
    Testing a valid user editing a message
    '''
    token, message_id, u_id, channel_id = setup_message

    updated_message = 'Hey everyone! How\'s it going?'
    assert message_edit(token, message_id, updated_message) == {}
    # Assumption - functions that act as voids return {}

    # Testing that searching for this message returns the updated message
    searched_message = search(token, 'Hey everyone! How\'s it going')['messages'][0]
    assert searched_message['message_id'] == message_id
    assert searched_message['message'] == updated_message

def test_invalidtoken_message_edit(setup_message):
    '''
    Testing editing a message with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = 5000

    updated_message = 'Hey everyone! How\'s it going?'

    with pytest.raises(AccessError) as _:
        message_edit(fake_token, message_id, updated_message)

def test_invalid_uid_message_edit(setup_message):
    '''
    Testing a different user editing than the one sending the message
    '''
    token, message_id, u_id, channel_id = setup_message

    # Logging out and registering a different user
    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    updated_message = 'I like python'

    with pytest.raises(AccessError) as _:
        message_edit(token, message_id, updated_message)

def test_invalid_messageid_message_edit(setup_message):
    '''
    Testing editing a message with an invalid messageID
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageId' # Assume all message Ids are numbers

    with pytest.raises(InputError) as _:
        updated_message = 'Hey everyone! How\'s it going?'
        message_edit(token, fake_message_id, updated_message)

def test_deleted_message_edit(setup_message):
    '''
    Testing that a messaged edited to an empty string is deleted
    '''
    token, message_id, u_id, channel_id = setup_message
    updated_message = ''

    message_edit(token, message_id, updated_message)

    # Test if the message list for the channel is now empty
    messages = channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 0

def test_long_message_edit(setup_message):
    '''
    Testing editing a message to longer than 1000 characters
    '''
    token, message_id, u_id, channel_id = setup_message

    with pytest.raises(InputError) as _:
        updated_message = 'x' * 1001
        message_edit(token, message_id, updated_message)

# Testing message remove function

def test_valid_message_remove(setup_message):
    '''
    Testing a successful removal of message
    '''
    token, message_id, u_id, channel_id = setup_message

    assert message_remove(token, message_id) == {}

    # Test if the message list for the channel is now empty
    messages = channel_messages(token, channel_id, 0)['messages']
    assert len(messages) == 0

def test_invalidtoken_message_remove(setup_message):
    '''
    Testing removing a message with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = 5000

    with pytest.raises(AccessError) as _:
        message_remove(fake_token, message_id)

def test_invalid_messageid_message_remove(setup_message):
    '''
    Testing trying to remove a message with an invalid id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageId'

    with pytest.raises(InputError) as _:
        message_remove(token, fake_message_id)

def test_invalid_uid_message_remove(setup_message):
    '''
    Testing a different user removing than the one who sent the message
    '''
    token, message_id, u_id, channel_id = setup_message

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    with pytest.raises(AccessError) as _:
        message_remove(token, message_id)

# Testing message react funciton

def test_message_react_valid(setup_message):
    '''
    Testing when a successful reaction to a message
    '''
    token, message_id, u_id, channel_id = setup_message

    message_react(token, message_id, 1)

    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['reacts'] == [{'is_this_user_reacted': True,
                                           'react_id': 1,
                                           'u_ids': [1]}]

def test_message_react_invalid_token(setup_message):
    '''
    Testing reacting to a message with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''

    with pytest.raises(AccessError) as _:
        message_react(fake_token, message_id, 1)

def test_message_react_invalid_reactid(setup_message):
    '''
    Testing reacting to a message with an invalid reactid (not 1)
    '''
    token, message_id, u_id, channel_id = setup_message

    with pytest.raises(InputError) as _:
        message_react(token, message_id, 2)

def test_message_react_invalid_messageid(setup_message):
    '''
    Testing reacting to a message with an invalid message_id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageID'

    with pytest.raises(InputError) as _:
        message_react(token, fake_message_id, 1)

def test_react_existing_react(setup_message):
    '''
    Testing reacting to the same message twice
    '''
    token, message_id, u_id, channel_id = setup_message

    message_react(token, message_id, 1)

    with pytest.raises(InputError):
        message_react(token, message_id, 1)

def test_invalud_uid_react(setup_message):
    '''
    Testing having a user react to a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    with pytest.raises(AccessError) as _:
        message_react(token, message_id, 1)

# Testing message unreact function

def test_message_unreact_valid(setup_message):
    '''
    Testing when a successful reaction to a message
    '''
    token, message_id, u_id, channel_id = setup_message

    message_react(token, message_id, 1)
    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['reacts'] == [{'is_this_user_reacted': True,
                                           'react_id': 1,
                                           'u_ids': [1]}]

    message_unreact(token, message_id, 1)
    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['reacts'] == []

def test_message_unreact_invalid_token(setup_message):
    '''
    Testing unreacting to a message with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''

    message_react(token, message_id, 1)

    with pytest.raises(AccessError) as _:
        message_unreact(fake_token, message_id, 1)

def test_message_unreact_invalid_reactid(setup_message):
    '''
    Testing reacting to a message with an invalid reactid (not 1)
    '''
    token, message_id, u_id, channel_id = setup_message

    message_react(token, message_id, 1)

    with pytest.raises(InputError) as _:
        message_unreact(token, message_id, 2)

def test_message_unreact_invalid_messageid(setup_message):
    '''
    Testing reacting to a message with an invalid message_id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageID'
    message_react(token, message_id, 1)

    with pytest.raises(InputError) as _:
        message_unreact(token, fake_message_id, 1)

def test_unreact_nonexisting_react(setup_message):
    '''
    Testing reacting to the same message twice
    '''
    token, message_id, u_id, channel_id = setup_message

    with pytest.raises(InputError):
        message_unreact(token, message_id, 1)

def test_invalid_uid_unreact(setup_message):
    '''
    Testing having a user react to a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message
    message_react(token, message_id, 1)

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    with pytest.raises(AccessError) as _:
        message_unreact(token, message_id, 1)

# Testing message pin function

def test_message_pin_valid(setup_message):
    '''
    Testing a successful pinning of a message
    '''
    token, message_id, u_id, channel_id = setup_message

    message_pin(token, message_id)

    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['is_pinned']

def test_message_pin_invalidtoken(setup_message):
    '''
    Testing pinning with a fake token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''

    with pytest.raises(AccessError) as _:
        message_pin(fake_token, message_id)

def test_message_pin_invalid_messageid(setup_message):
    '''
    Testing pinning with an invalid message id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageID'

    with pytest.raises(InputError) as _:
        message_pin(token, fake_message_id)

def test_message_pin_already_pinned(setup_message):
    '''
    Testing pinning a message that is already pinned
    '''
    token, message_id, u_id, channel_id = setup_message
    message_pin(token, message_id)

    with pytest.raises(InputError) as _:
        message_pin(token, message_id)

def test_message_pin_invalid_uid(setup_message):
    '''
    Testing having a user pin a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    with pytest.raises(AccessError) as _:
        message_pin(token, message_id)

# Testing message unpin function

def test_message_unpin_valid(setup_message):
    '''
    Testing a successful unpinning of a message
    '''
    token, message_id, u_id, channel_id = setup_message

    message_pin(token, message_id)
    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['is_pinned']

    message_unpin(token, message_id)

    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert not searched_message['is_pinned']

def test_message_unpin_invalidtoken(setup_message):
    '''
    Testing unpinning with a fake token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''
    message_pin(token, message_id)

    with pytest.raises(AccessError) as _:
        message_unpin(fake_token, message_id)

def test_message_unpin_invalid_messageid(setup_message):
    '''
    Testing unpinning with an invalid message id
    '''
    token, message_id, u_id, channel_id = setup_message
    message_pin(token, message_id)
    fake_message_id = 'fakeMessageID'

    with pytest.raises(InputError) as _:
        message_unpin(token, fake_message_id)

def test_message_unpin_not_pinned(setup_message):
    '''
    Testing unpinning a message that is already pinned
    '''
    token, message_id, u_id, channel_id = setup_message

    with pytest.raises(InputError) as _:
        message_unpin(token, message_id)

def test_message_unpin_invalid_uid(setup_message):
    '''
    Testing having a user unpin a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message
    message_pin(token, message_id)

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    with pytest.raises(AccessError) as _:
        message_unpin(token, message_id)

# Testing message_sendlater

def test_valid_message_sendlater_later(setup_channel):
    '''
    Testing sending a valid message that is sent a long while after being created
    Message will not show up in search
    '''
    token, channel_id, _ = setup_channel
    sendtime = time() + 2

    message_results = message_sendlater(token, channel_id, 'It is a nice day', sendtime)

    # Testing that the new message has a message ID
    assert message_results['message_id'] == 1

    # Testing that searching for this message DOES NOT return the updated message
    searched_messages = search(token, 'It is a nice day')['messages']
    assert len(searched_messages) == 0

    sleep(3)
    searched_message = search(token, 'It is a nice day')['messages'][0]
    assert searched_message['message'] == 'It is a nice day'

def test_valid_message_sendlater_past(setup_channel):
    '''
    Testing a valid message that is sent in the past
    '''
    token, channel_id, _ = setup_channel
    sendtime = time() - 1

    with pytest.raises(InputError) as _:
        message_results = message_sendlater(token, channel_id, 'Hey everyone', sendtime)

def test_long_message_sendlater(setup_channel):
    '''
    Testing sending a message later that is longer than 1000 characters
    '''

    token, channel_id, u_id = setup_channel
    sendtime = time() + 1000

    with pytest.raises(InputError) as _:
        long_message = 'x' * 1001
        message_id = message_sendlater(token, channel_id, long_message, sendtime)

def test_unjoined_channel_message_sendlater(setup_channel):
    '''
    Testing sending message later when the user hasn't joined the channel
    '''
    token, channel_id, u_id = setup_channel
    sendtime = time() + 1000

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    unjoined_channel_id = channels_create(token, 'A Second Channel', False)['channel_id']
    auth_logout(token)

    token = auth_login('z5169779@ad.unsw.edu.au', 'abc123')['token']

    with pytest.raises(AccessError) as _:
        message_id = message_sendlater(token, unjoined_channel_id, 'Hey everyone', sendtime)

def test_invalid_token_message_sendlater(setup_channel):
    '''
    Testing sending a message later with an invalid token
    '''

    fake_token, channel_id = '', setup_channel[1]
    sendtime = time() + 1000

    with pytest.raises(AccessError) as _:
        message_id = message_sendlater(fake_token, channel_id, 'Hey everyone', sendtime)

def test_invalid_id_message_sendlater(setup_channel):
    '''
    Testing sending a message later with an invalid channel ID
    '''

    token, fake_channel_id = setup_channel[0], 'fakeId'
    sendtime = time() + 1000

    with pytest.raises(InputError) as _:
        message_id = message_sendlater(token, fake_channel_id, 'Hey everyone', sendtime)
