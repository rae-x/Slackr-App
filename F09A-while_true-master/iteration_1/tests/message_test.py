import pytest
from message import message_send, message_edit, message_remove
from auth import auth_register, auth_logout
from channels import channels_create
from channel import channel_join, channel_addowner, channel_removeowner
from other import search
from error import InputError, AccessError

@pytest.fixture
def setup_channel():
    # Registers a new user, creates a new channel and adds them to that channel
    # Assumption - user is not automatically added to a channel when the channel is created
    register_results = auth_register('z5169779@ad.unsw.edu.au', 'abc123', 'Joe', 'Bloggs')
    token = register_results['token']
    u_id = register_results['u_id']

    new_channel = channels_create(token, 'My First Channel', True)
    channel_join(token, new_channel['channel_id'])
    channel_addowner(token, new_channel['channel_id'], u_id)

    return token, new_channel['channel_id'], u_id

### Testing message_send function

def test_valid_message_send(setup_channel):
    # Testing a valid message
    token, channel_id, u_id = setup_channel

    message_results = message_send(token, channel_id, 'Hey everyone')

    # Testing that the new message has a message ID
    assert message_results['message_id'] == 1

    # Testing that searching for this message returns the updated message
    searched_message = search(token, 'Hey everyone')['messages'][0]
    assert searched_message['message_id'] == 1
    assert searched_message['message'] == 'Hey everyone'

def test_long_message_send(setup_channel):
    # Testing a message that is longer than 1000 characters

    token, channel_id, u_id = setup_channel

    with pytest.raises(InputError) as e:
        long_message = 'x' * 1001
        message_id = message_send(token, channel_id, long_message)

def test_unjoined_channel_message_send(setup_channel):
    token, channel_id = setup_channel[0], '2'

    with pytest.raises(AccessError) as e:
        message_id = message_send(token, channel_id, 'Hey everyone')

def test_invalid_token_message_send(setup_channel):
    # Testing sending a message with an invalid token

    fake_token, channel_id = '', setup_channel[1]

    with pytest.raises(AccessError) as e:
        message_id = message_send(fake_token, channel_id, 'Hey everyone')

def test_invalid_id_message_send(setup_channel):
    # Testing sending a message with an invalid channel ID

    token, fake_channel_id = setup_channel[0], 'fakeId'

    with pytest.raises(AccessError) as e:
        message_id = message_send(token, fake_channel_id, 'Hey everyone')

### Testing message_edit function

@pytest.fixture
def setup_message(setup_channel):
    # Registers a new user, creates a new channel and adds the user to the channel using setup_channe;
    # Sends a message to the channel
    token, channel_id, u_id = setup_channel

    new_message = message_send(token, channel_id, 'Hey everyone')
    return token, new_message['message_id'], u_id, channel_id

def test_valid_message_edit(setup_message):
    # Testing a valid user editing a message
    token, message_id, u_id, channel_id = setup_message

    updated_message = 'Hey everyone! How\'s it going?'
    assert message_edit(token, message_id, updated_message) == {}
    # Assumption - functions that act as voids return {}

    # Testing that searching for this message returns the updated message
    searched_message = search(token, 'Hey everyone! How\'s it going')['messages'][0]
    assert searched_message['message_id'] == message_id
    assert searched_message['message'] == updated_message

def test_invalid_uid_message_edit(setup_message):
    # Testing a different user editing than the one sending the message
    token, message_id, u_id, channel_id = setup_message

    # Logging out and registering a different user
    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    updated_message = 'I like python'

    with pytest.raises(AccessError) as e:
        message_edit(token, message_id, updated_message)

def test_non_admin_message_edit(setup_message):
    # Testing a user editing a message who is not a channel owner
    token, message_id, u_id, channel_id = setup_message
    channel_removeowner(token, channel_id, u_id)

    with pytest.raises(AccessError) as e:
        updated_message = 'Hey everyone! How\'s it going?'
        message_edit(token, message_id, updated_message)

def test_invalid_messageid_message_edit(setup_message):
    # Testing editing a message with an invalid messageID
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageId' # Assume all message Ids are numbers

    with pytest.raises(InputError) as e:
        updated_message = 'Hey everyone! How\'s it going?'
        message_edit(token, fake_message_id, updated_message)

def test_deleted_message_edit(setup_message):
    # Testing that a messaged edited to an empty string is deleted
    token, message_id, u_id, channel_id = setup_message

    updated_message = ''

    message_edit(token, message_id, updated_message)
    assert search(token, updated_message)['messages'] == []

def test_long_message_edit(setup_message):
    # Testing editing a message to longer than 1000 characters
    token, message_id, u_id, channel_id = setup_message

    with pytest.raises(InputError) as e:
        updated_message = 'x' * 1001
        message_edit(token, message_id, updated_message)

# Testing message remove function

def test_valid_message_remove(setup_message):
    # Testing a successful removal of message
    token, message_id, u_id, channel_id = setup_message

    assert message_remove(token, message_id) == {}

def test_invalid_messageid_message_remove(setup_message):
    # Testing trying to remove a message with an invalid id
    token, message_id, u_id, channel_id = setup_message
    fake_message_id = 'fakeMessageId'

    with pytest.raises(InputError) as e:
        message_remove(token, fake_message_id)

def test_invalid_uid_message_remove(setup_message):
    # Testing a different user removing than the one who sent the message
    token, message_id, u_id, channel_id = setup_message

    auth_logout(token)
    new_user = auth_register('nick.p@iinet.net.au', 'abc123', 'Joe', 'Public')
    token = new_user['token']
    u_id = new_user['u_id']

    with pytest.raises(AccessError) as e:
        message_remove(token, message_id)

def test_non_admin_message_remove(setup_message):
    # Testing a user removing a message who is not a channel owner
    token, message_id, u_id, channel_id = setup_message
    channel_removeowner(token, channel_id, u_id)

    with pytest.raises(AccessError) as e:
        message_remove(token, message_id) == {}
