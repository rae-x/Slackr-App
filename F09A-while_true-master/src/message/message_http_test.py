'''
message_http_test.py

Tests all the routes for /channels
- /message/send
- /message/edit
- /message/remove
- /message/sendlater
- /message/react
- /message/unreact
- /message/pin
- /message/unpin
'''

# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable

from time import time, sleep
import json
import pytest
import requests
from http_test import APP_URL

@pytest.fixture(autouse=True)
def call_workspace_reset():
    '''
    Automatic fixture to reset state between tests
    '''
    requests.post(APP_URL + "/workspace/reset")

@pytest.fixture
def setup_channel():
    '''
    Setups a user and returns a dictionary of the user's ID and token
    '''
    payload = {"email": "johncitizen@hotmail.com",
               "password": "abcdef1",
               "name_first": "John",
               "name_last": "Citizen"}
    response = requests.post(f"{APP_URL}/auth/register", json=payload)
    data = response.json()
    token = data["token"]
    u_id = data['u_id']

    payload = {'token':token, 'name':'My First Channel', 'is_public': True}
    response = requests.post(f'{APP_URL}/channels/create', json=payload)
    data = response.json()

    return token, data['channel_id'], u_id

# Testing /message/send

def test_valid_message_send(setup_channel):
    '''
    Testing sending a valid message
    '''
    token, channel_id, _ = setup_channel

    payload = {'token': token,
               'channel_id': channel_id,
               'message': 'Hey everyone'}

    response = requests.post(f'{APP_URL}/message/send', json=payload)
    data = response.json()

    # Testing that the new message has a message id
    assert data['message_id'] == 1

    # Testing that searching for this message returns the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = json.loads(response.text)['messages'][0]
    assert searched_message['message_id'] == 1
    assert searched_message['message'] == 'Hey everyone'

def test_long_message_send(setup_channel):
    '''
    Testing a message that is longer than 1000 characters
    '''
    token, channel_id, _ = setup_channel
    long_message = 'x' * 1001

    payload = {'token': token,
               'channel_id': channel_id,
               'message': long_message}

    response = requests.post(f'{APP_URL}/message/send', json=payload)

    assert response.status_code == 400
    assert 'Message is more than 1000 characters long' in response.text

def test_unjoined_channel_message_send(setup_channel):
    '''
    Testing sending message when the user hasn't joined the channel
    '''
    token, _, _ = setup_channel

    # Log out, registers as a new user and send a message to a new channel
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    channel_payload = {'token':token, 'name':'2nd channel', 'is_public': True}
    response = requests.post(f'{APP_URL}/channels/create', json=channel_payload)
    unjoined_channel_id = response.json()['channel_id']

    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)

    login_payload = {'email':'johncitizen@hotmail.com', 'password':'abcdef1'}
    response = requests.post(f'{APP_URL}/auth/login', json=login_payload)
    token = response.json()['token']

    payload = {'token':token,
               'channel_id':unjoined_channel_id,
               'message':'Hello there'}
    response = requests.post(f'{APP_URL}/message/send', json=payload)

    assert response.status_code == 400
    assert 'User is not in the channel they are posting to' in response.text

def test_invalid_token_message_send(setup_channel):
    '''
    Testing sending a message with an invalid token
    '''
    fake_token, channel_id = '', setup_channel[1]

    payload = {'token': fake_token,
               'channel_id': channel_id,
               'message': 'Hey everyone'}

    response = requests.post(f'{APP_URL}/message/send', json=payload)

    assert response.status_code == 400 and 'invalid token' in response.text

def test_invalid_id_message_send(setup_channel):
    '''
    Testing sending a message with an invalid channel ID
    '''
    token, fake_channel_id = setup_channel[0], 5000

    payload = {'token': token,
               'channel_id': fake_channel_id,
               'message': 'Hey everyone'}

    response = requests.post(f'{APP_URL}/message/send', json=payload)

    assert response.status_code == 400 and 'invalid channel ID' in response.text

# Testing message/edit

@pytest.fixture
def setup_message(setup_channel):
    '''
    Registers a new user, creates a new channel and adds
    the user to the channel using setup_channel
    Sends a message to the channel
    '''
    token, channel_id, u_id = setup_channel

    payload = {'token': token,
               'channel_id': channel_id,
               'message': 'Hey everyone'}

    response = requests.post(f'{APP_URL}/message/send', json=payload)
    data = response.json()

    return token, data['message_id'], u_id, channel_id

def test_valid_message_edit(setup_message):
    '''
    Testing a valid user editing a message
    '''
    token, message_id, u_id, channel_id = setup_message
    updated_message = 'Hey everyone! How\'s it going?'

    payload = {'token': token,
               'message_id': channel_id,
               'message': updated_message}

    response = requests.put(f'{APP_URL}/message/edit', json=payload)
    data = response.json()
    assert data == {}

    # Testing that searching for this message returns the updated message
    get_payload = {'token':token, 'query_str':'Hey everyone! How\'s it going?'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = json.loads(response.text)['messages'][0]
    assert searched_message['message_id'] == 1
    assert searched_message['message'] == updated_message

def test_invalid_uid_message_edit(setup_message):
    '''
    Testing a different user editing than the one sending the message
    '''
    token, message_id, u_id, channel_id = setup_message
    updated_message = 'Hey everyone! How\'s it going?'

    # Log out, registers as a new user and tries to edit a message
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    payload = {'token': token,
               'message_id': message_id,
               'message': updated_message}
    response = requests.put(f'{APP_URL}/message/edit', json=payload)

    assert response.status_code == 400
    assert 'User did not send the message they are trying to edit' in response.text

def test_invalid_messageid_message_edit(setup_message):
    '''
    Testing editing a message with an invalid messageID
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageId'
    updated_message = 'Hey everyone! How\'s it going?'

    payload = {'token': token,
               'message_id': fake_message_id,
               'message': updated_message}

    response = requests.put(f'{APP_URL}/message/edit', json=payload)
    assert response.status_code == 400 and 'Message ID does not exist' in response.text

def test_deleted_message_edit(setup_message):
    '''
    Testing that a messaged edited to an empty string is deleted
    '''
    token, message_id, u_id, channel_id = setup_message
    updated_message = ''

    payload = {'token': token,
               'message_id': message_id,
               'message': updated_message}

    requests.put(f'{APP_URL}/message/edit', json=payload)
    payload = {'token':token, 'channel_id':channel_id, 'start':0}
    response = requests.get(f'{APP_URL}/channel/messages', params=payload)
    messages = response.json()['messages']
    assert len(messages) == 0

def test_long_message_edit(setup_message):
    '''
    Testing editing a message to longer than 1000 characters
    '''
    token, message_id, u_id, channel_id = setup_message
    updated_message = 'x' * 1001

    payload = {'token': token,
               'message_id': message_id,
               'message': updated_message}

    response = requests.put(f'{APP_URL}/message/edit', json=payload)
    assert response.status_code == 400
    assert 'Message is more than 1000 characters long' in response.text

# Testing message/remove

def test_valid_message_remove(setup_message):
    '''
    Testing a successful removal of message
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id}
    response = requests.delete(f'{APP_URL}/message/remove', json=payload)
    data = response.json()
    assert data == {}

    # Test if the message list for the channel is now empty
    payload = {'token':token, 'channel_id':channel_id, 'start':0}
    response = requests.get(f'{APP_URL}/channel/messages', params=payload)
    messages = response.json()['messages']
    assert len(messages) == 0

def test_invalidid_messageid_message_remove(setup_message):
    '''
    Testing trying to remove a message with an invalid id
    '''

    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 5000

    payload = {'token':token, 'message_id':fake_message_id}
    response = requests.delete(f'{APP_URL}/message/remove', json=payload)

    assert response.status_code == 400
    assert 'Message ID does not exist' in response.text

def test_invalid_uid_message_remove(setup_message):
    '''
    Testing a different user removing than the one who sent the message
    '''
    token, message_id, u_id, channel_id = setup_message

    # Log out, registers as a new user and tries to remove a message
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    payload = {'token': token, 'message_id': message_id}
    response = requests.delete(f'{APP_URL}/message/remove', json=payload)

    assert response.status_code == 400
    assert 'User did not send the message they are trying to remove' in response.text

# Testing message/react

def test_message_react_valid(setup_message):
    '''
    Testing when a successful reaction to a message
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)

    # Testing that searching for this message returns the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = json.loads(response.text)['messages'][0]
    assert searched_message['reacts'] == [{'is_this_user_reacted': True,
                                           'react_id': 1,
                                           'u_ids': [1]}]

def test_message_react_invalid_token(setup_message):
    '''
    Testing reacting to a message with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''

    payload = {'token':fake_token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)
    assert response.status_code == 400 and 'invalid token' in response.text


def test_message_react_invalid_reactid(setup_message):
    '''
    Testing reacting to a message with an invalid reactid (not 1)
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id, 'react_id': 2}
    response = requests.post(f'{APP_URL}/message/react', json=payload)
    assert response.status_code == 400 and 'React ID is invalid' in response.text

def test_message_react_invalid_messageid(setup_message):
    '''
    Testing reacting to a message with an invalid message_id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 5000

    payload = {'token':token, 'message_id':fake_message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)
    assert response.status_code == 400 and \
    'Message ID does not exist' in response.text

def test_react_existing_react(setup_message):
    '''
    Testing reacting to the same message twice
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    requests.post(f'{APP_URL}/message/react', json=payload)
    # Post the react again
    response = requests.post(f'{APP_URL}/message/react', json=payload)
    assert response.status_code == 400
    assert 'Message already contains a react with that ID'

def test_invalid_uid_react(setup_message):
    '''
    Testing having a user react to a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message

    # Log out, registers as a new user and tries to react to a message
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    # Post a react while not being in the channel
    payload = {'token': token, 'message_id': message_id, 'react_id':1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)
    assert response.status_code == 400
    assert 'User is not in the channel they are reacting to' in response.text

# Testing message/unreact

def test_message_unreact_valid(setup_message):
    '''
    Testing when a successful un-reaction to a message
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)

    # Testing that searching for this message returns the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = json.loads(response.text)['messages'][0]
    assert searched_message['reacts'] == [{'is_this_user_reacted': True,
                                           'react_id': 1,
                                           'u_ids': [1]}]

    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/unreact', json=payload)

    # Testing that searching for this message returns the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = json.loads(response.text)['messages'][0]
    assert searched_message['reacts'] == []


def test_message_unreact_invalid_token(setup_message):
    '''
    Testing un-reacting to a message with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''

    # React to the message
    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)

    # Un-react with the invalid token
    payload = {'token':fake_token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/unreact', json=payload)
    assert response.status_code == 400
    assert 'invalid token' in response.text


def test_message_unreact_invalid_reactid(setup_message):
    '''
    Testing un-reacting to a message with an invalid reactid (not 1)
    '''
    token, message_id, u_id, channel_id = setup_message

    # React to the message
    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)

    # Unreact
    payload = {'token':token, 'message_id':message_id, 'react_id': 2}
    response = requests.post(f'{APP_URL}/message/unreact', json=payload)
    assert response.status_code == 400 and 'React ID is invalid' in response.text

def test_message_unreact_invalid_messageid(setup_message):
    '''
    Testing un-reacting to a message with an invalid message_id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 5000
    # React to the message
    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)

    # Unreact with invalid message id
    payload = {'token':token, 'message_id':fake_message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)
    assert response.status_code == 400
    assert 'Message ID does not exist' in response.text

def test_unreact_nonexisting_react(setup_message):
    '''
    Testing unreacting to a message that was not reacted to
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/unreact', json=payload)
    assert response.status_code == 400
    assert 'Message does not contain a react with that ID' in response.text

def test_invalid_uid_unreact(setup_message):
    '''
    Testing having a user unreact to a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message
    # React to the message
    payload = {'token':token, 'message_id':message_id, 'react_id': 1}
    response = requests.post(f'{APP_URL}/message/react', json=payload)

    # Log out, registers as a new user and tries to unreact to a message
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    # Post a un-react while not being in the channel
    payload = {'token': token, 'message_id': message_id, 'react_id':1}
    response = requests.post(f'{APP_URL}/message/unreact', json=payload)
    assert response.status_code == 400
    #assert 'User is not in the channel they are un-reacting to' in response.text
    assert 'User is not in the channel they are un-reacting to' in response.text

# Testing message/pin

def test_message_pin_valid(setup_message):
    '''
    Testing a successful pinning of a message
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    # Testing that searching for this message returns the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = response.json()['messages'][0]
    assert searched_message['is_pinned']

def test_message_pin_invalid_token(setup_message):
    '''
    Testing pinning with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''

    payload = {'token':fake_token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    assert response.status_code == 400
    assert 'invalid token' in response.text

def test_message_pin_invalid_messageid(setup_message):
    '''
    Testing pinning a message with an invalid message_id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 5000

    payload = {'token':token, 'message_id':fake_message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    assert response.status_code == 400
    assert 'Message ID does not exist' in response.text

def test_message_pin_already_pinned(setup_message):
    '''
    Testing pinning a message that is already pinned
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id}
    requests.post(f'{APP_URL}/message/pin', json=payload)

    # Pin the react again
    response = requests.post(f'{APP_URL}/message/pin', json=payload)
    assert response.status_code == 400 and 'Message is already pinned'

def test_invalid_uid_pin(setup_message):
    '''
    Testing having a user pin a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message

    # Log out, registers as a new user and tries to pin a message
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    # Pin a message
    payload = {'token': token, 'message_id': message_id, 'react_id':1}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    assert response.status_code == 400
    assert 'User is not in the channel they are pinning on' in response.text

# Testing message/unpin

def test_message_unpin_valid(setup_message):
    '''
    Testing a successful unpinning of a message
    '''
    token, message_id, u_id, channel_id = setup_message

    # Pin the message
    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    # Testing that searching for this message returns the pinned message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = response.json()['messages'][0]
    assert searched_message['is_pinned']

    # Unpin the message
    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/unpin', json=payload)

    # Testing that searching for this message returns the unpinned message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = response.json()['messages'][0]
    assert not searched_message['is_pinned']

def test_message_unpin_invalid_token(setup_message):
    '''
    Testing unpinning with an invalid token
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_token = ''
    # Pin the message
    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    payload = {'token':fake_token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/unpin', json=payload)
    assert response.status_code == 400 and 'invalid token' in response.text

def test_message_unpin_invalid_messageid(setup_message):
    '''
    Testing unpinning a message with an invalid message_id
    '''
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 5000
    # Pin the message
    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    payload = {'token':token, 'message_id':fake_message_id}
    response = requests.post(f'{APP_URL}/message/unpin', json=payload)
    assert response.status_code == 400 and 'Message ID does not exist' in response.text

def test_message_unpin_not_pinned(setup_message):
    '''
    Testing unpinning a message that is not pinned
    '''
    token, message_id, u_id, channel_id = setup_message

    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/unpin', json=payload)
    assert response.status_code == 400 and 'Message is already unpinned'

def test_invalid_uid_unpin(setup_message):
    '''
    Testing having a user unpin a message who is not in the channel
    '''
    token, message_id, u_id, channel_id = setup_message
    # Pin the message
    payload = {'token':token, 'message_id':message_id}
    response = requests.post(f'{APP_URL}/message/pin', json=payload)

    # Log out, registers as a new user and tries to pin a message
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    # Attempt to unpin a message
    payload = {'token': token, 'message_id': message_id}
    response = requests.post(f'{APP_URL}/message/unpin', json=payload)

    assert response.status_code == 400
    assert 'User is not in the channel they are unpinning on' in response.text

# Testing message/sendlater

def test_valid_message_sendlater_later(setup_channel):
    '''
    Testing sending a valid message that is sent a long while after being created
    Message will not show up in search
    '''
    token, channel_id, _ = setup_channel
    sendtime = time() + 2

    payload = {'token':token,
               'channel_id':channel_id,
               'message':'Hey everyone',
               'time_sent':sendtime}

    response = requests.post(f'{APP_URL}/message/sendlater', json=payload)
    data = response.json()
    assert data['message_id'] == 1

    # Testing searching for the message does not return the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_messages = response.json()['messages']
    assert len(searched_messages) == 0

    # Sleep for a moment
    sleep(3)

    # Searching for the message returns the message
    get_payload = {'token':token, 'query_str':'Hey everyone'}
    response = requests.get(f'{APP_URL}/search', params=get_payload)
    searched_message = response.json()['messages'][0]
    assert searched_message['message'] == 'Hey everyone'


def test_valid_message_sendlater_past(setup_channel):
    '''
    Testing a valid message that is sent in the past
    '''
    token, channel_id, _ = setup_channel
    sendtime = time() - 1

    payload = {'token':token,
               'channel_id':channel_id,
               'message':'Hey everyone',
               'time_sent':sendtime}

    response = requests.post(f'{APP_URL}/message/sendlater', json=payload)
    assert response.status_code == 400 and 'Time sent is a time in the past'


def test_long_message_sendlater(setup_channel):
    '''
    Testing sending a message later that is longer than 1000 characters
    '''
    token, channel_id, _ = setup_channel
    sendtime = time() + 1
    long_message = 'x' * 1001

    payload = {'token':token,
               'channel_id':channel_id,
               'message':long_message,
               'sendtime':sendtime}

    response = requests.post(f'{APP_URL}/message/sendlater', json=payload)
    assert response.status_code == 400 and 'Message is more than 1000 characters long'

def test_unjoined_channel_message_sendlater(setup_channel):
    '''
    Testing sending a message later when the user hasn't joined the channel
    '''
    token, channel_id, u_id = setup_channel
    sendtime = time() + 1000

    # Log out, registers as a new user and send a message to a new channel
    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)
    user_2 = {"email": "nick.p@iinet.net.au",
              "password": "abcdef1",
              "name_first": "John",
              "name_last": "Citizen2"}

    response = requests.post(f'{APP_URL}/auth/register', json=user_2)
    data = response.json()
    token = data['token']

    channel_payload = {'token':token, 'name':'2nd channel', 'is_public': True}
    response = requests.post(f'{APP_URL}/channels/create', json=channel_payload)
    unjoined_channel_id = response.json()['channel_id']

    payload = {'token':token}
    requests.post(f'{APP_URL}/auth/logout', json=payload)

    login_payload = {'email':'johncitizen@hotmail.com', 'password':'abcdef1'}
    response = requests.post(f'{APP_URL}/auth/login', json=login_payload)
    token = response.json()['token']

    payload = {'token':token,
               'channel_id':unjoined_channel_id,
               'message':'Hello there',
               'time_sent':sendtime}
    response = requests.post(f'{APP_URL}/message/sendlater', json=payload)

    assert response.status_code == 400
    assert 'User is not in the channel they are posting to' in response.text

def test_invalid_token_message_sendlater(setup_channel):
    '''
    Testing sending a message later with an invalid token
    '''
    token, channel_id, u_id = setup_channel
    sendtime = time() + 1000
    fake_token = ''

    payload = {'token': fake_token,
               'channel_id': channel_id,
               'message': 'Hey everyone',
               'time_sent':sendtime}

    response = requests.post(f'{APP_URL}/message/sendlater', json=payload)
    assert response.status_code == 400 and 'invalid token' in response.text

def test_invalid_id_messagesendlater(setup_channel):
    '''
    Testing sending a message later with an invalid channel ID
    '''
    token, channel_id, u_id = setup_channel
    sendtime = time() + 1000
    fake_channel_id = 5000

    payload = {'token': token,
               'channel_id': fake_channel_id,
               'message': 'Hey everyone',
               'time_sent':sendtime}

    response = requests.post(f'{APP_URL}/message/sendlater', json=payload)
    assert response.status_code == 400 and 'invalid channel ID' in response.text
