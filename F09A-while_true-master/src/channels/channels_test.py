'''
channels_test.py

Test all functions in channels.py
- channels_list
- channels_create
- channels_listall

'''

# pylint: disable=redefined-outer-name

# Builtin/pip modules
import pytest
# Core package modules
from error import InputError, AccessError
# Functions to help with setup
from workspace_reset import workspace_reset
from channels import channels_list, channels_create, channels_listall
from auth import auth_register

@pytest.fixture(autouse=True)
def call_workspace_reset():
    '''
    auto fixture to reset between tests
    '''
    workspace_reset()

@pytest.fixture
def setup_user():
    '''
    Sets up the data store to be used and clears it
    '''
    # Registers a new user
    register_results = auth_register('z5169779@ad.unsw.edu.au', 'abc123', 'Joe', 'Bloggs')
    token = register_results['token']

    return token

def test_channels_list_empty(setup_user):
    '''
    Tests for user not in any channel
    '''
    token = setup_user
    assert channels_list(token) == {'channels': []}

def test_channels_list_invalid_token():
    '''
    Tests for access error from an invalid token
    '''
    with pytest.raises(AccessError):
        channels_list("invalidtoken")

def test_channels_list_public(setup_user):
    '''
    Tests correct return value for user in 1 public channel
    '''
    token = setup_user

    #Get the channel id for the first channel, which is public
    channels_create(token, 'First channel', True)

    #Check that channel list prints out the correct data
    assert channels_list(token) == {
        'channels': [
            {'channel_id': 1,
             'name': 'First channel'}
        ]
    }

def test_channels_list_multiple(setup_user):
    '''
    Tests for correct return value when user is in a few channels.
    '''
    token = setup_user

    #Get the channel id for the first and second channel, which is public
    channels_create(token, 'First channel', True)
    channels_create(token, 'Second channel', True)

    #Check that channel list prints out the correct data
    assert channels_list(token) == {
        'channels':[
            {'channel_id': 1,
             'name': 'First channel'},
            {'channel_id': 2,
             'name': 'Second channel'}
            ]
    }

def test_channels_listall(setup_user):
    '''
    Testing the channels_listall function
    '''

    token = setup_user

    # No channels added
    assert channels_listall(token) == {'channels':[]}

    # Testing adding 1 channel
    channels_create(token, 'My First Channel', False)
    assert channels_listall(token) == {
        'channels': [
            {'channel_id': 1,
             'name': 'My First Channel'}
        ]
    }

    # Testing adding a second channel
    channels_create(token, 'My 2nd Channel', True)
    assert channels_listall(token) == {
        'channels': [
            {'channel_id': 1,
             'name': 'My First Channel'},
            {'channel_id': 2,
             'name': 'My 2nd Channel'}
            ]
        }

def test_channels_listall_invalid_token(setup_user):
    '''
    Testing listing all channels with an invalid token
    '''
    _ = setup_user
    fake_token = ''

    with pytest.raises(AccessError) as _:
        channels_listall(fake_token)

def test_channels_create_public(setup_user):
    '''
    Testing creating a public channel
    '''

    token = setup_user
    ## ASSUMPTION - registering automatically logs you in (as you get a token)

    new_channel = channels_create(token, 'My First Channel', True)

    # Testing that the new channel has a channel_id => assuming ID can never be an empty string
    # Assuming channels are numbered in order of creation
    assert new_channel['channel_id'] == 1

def test_channels_create_private(setup_user):
    '''# Testing creating a valid private channel'''

    token = setup_user

    new_channel = channels_create(token, 'My First Channel', False)

    # Testing that the new channel has a channel_id
    assert new_channel['channel_id'] == 1

def test_channels_create_public_long(setup_user):
    '''
    Testing creating a public channel with a name > 20 chrs long
    '''
    token = setup_user

    with pytest.raises(InputError) as _:
        channels_create(token, 'This Channel Name > 20 Chrs Long', True)

def test_channels_create_private_long(setup_user):
    '''
    Tests a private channel with name that is more than 20 chrs long
    '''
    token = setup_user

    with pytest.raises(InputError) as _:
        channels_create(token, 'This Channel Name is Way More than 20 Chrs Long', False)

def test_invalid_token_channels_create_public(setup_user):
    '''
    Testing attempting to create a public channel with an invalid token
    '''
    _ = setup_user
    fake_token = ''

    with pytest.raises(AccessError) as _:
        channels_create(fake_token, 'My First Channel', True)

def test_invalid_token_channels_create_private(setup_user):
    '''
    Testing attempting to create a private channel with an invalid token
    '''
    _ = setup_user
    fake_token = ''

    with pytest.raises(AccessError) as _:
        channels_create(fake_token, 'My First Channel', False)
