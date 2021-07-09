from channels import channels_create, channels_listall
from auth import auth_register
from error import InputError, AccessError
import pytest

@pytest.fixture
def setup_user():
    # Registers a new user
    register_results = auth_register('z5169779@ad.unsw.edu.au', 'abc123', 'Joe', 'Bloggs')
    token = register_results['token']
    # u_id = register_results['u_id']

    return token

def test_channels_create_public(setup_user):
    # Testing creating a public channel

    token = setup_user
    ## ASSUMPTION - registering automatically logs you in (as you get a token)

    new_channel = channels_create(token, 'My First Channel', True)

    # Testing that the new channel has a channel_id => assuming ID can never be an empty string
    # Assuming channels are numbered in order of creation
    assert new_channel['channel_id'] == 1
    assert new_channel['name'] == 'My First Channel'
    assert new_channel['is_public']

def test_channels_create_private(setup_user):
    # Testing creating a valid private channel

    token = setup_user

    new_channel = channels_create(token, 'My First Channel', False)

    # Testing that the new channel has a channel_id
    assert new_channel['channel_id'] == 1
    assert new_channel['name'] == 'My First Channel'
    assert not new_channel['is_public']

def test_channels_create_public_long(setup_user):
    # Tests a public channel with name that is more than 20 chrs long
    token = setup_user

    with pytest.raises(InputError) as e:
        error_channel = channels_create(token, 'This Channel Name is Way More than 20 Chrs Long', True)

def test_channels_create_private_long(setup_user):
    # Tests a private channel with name that is more than 20 chrs long
    token = setup_user

    with pytest.raises(InputError) as e:
        error_channel = channels_create(token, 'This Channel Name is Way More than 20 Chrs Long', False)

def test_invalid_token_channels_create_public(setup_user):
    # Testing attempting to create a public channel with an invalid token
    fake_token = ''

    with pytest.raises(AccessError) as e:
        error_channel = channels_create(fake_token, 'My First Channel', True)

def test_invalid_token_channels_create_private(setup_user):
    # Testing attempting to create a private channel with an invalid token
    fake_token = ''

    with pytest.raises(AccessError) as e:
        error_channel = channels_create(fake_token, 'My First Channel', False)

def test_channels_listall(setup_user):
    # Testing the channels_listall function

    token = setup_user

    # No channels added
    assert channels_listall(token) == {'channels':[]}

    # Testing adding 1 channel
    first_channel = channels_create(token, 'My First Channel', False)
    assert channels_listall(token) == {
        'channels': [
            { 'channel_id': 1,
            name: 'My First Channel',
            public: False}
        ]
    }

    # Testing adding a second channel
    second_channel = channels_create(token, 'My 2nd Channel', True)
    assert channels_listall(token) == {
        'channels': [
            { 'channel_id': 1,
            name: 'My First Channel',
            public: False},
            { 'channel_id': 2,
            name: 'My 2nd Channel',
            public: True}
        ]
    }
