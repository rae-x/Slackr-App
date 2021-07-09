'''
channels_http_test.py

Tests all the routes for /channels
- /channels/create
- /channels/listall
- /channels/list
'''

# pylint: disable=redefined-outer-name

# Builtin/pip modules
import json
import pytest
import requests
# Package modules
from http_test import APP_URL

@pytest.fixture(autouse=True)
def call_workspace_reset():
    '''
    Automatic fixture to reset state between tests
    '''
    requests.post(APP_URL + "/workspace/reset")

@pytest.fixture
def setup_user():
    '''
    Setups a user and returns a dictionary of the user's ID and token
    '''
    payload = {"email": "johncitizen@hotmail.com",
               "password": "abcdef1",
               "name_first": "John",
               "name_last": "Citizen"}
    response = requests.post(APP_URL + "/auth/register", json=payload)
    data = response.json()

    return data["token"]

def call_channels_create(token, name, is_public):
    '''
    call channels create to create a new channel
    '''
    payload = {"token": token, "name": name, "is_public": is_public}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)
    return data["channel_id"]

# Testing /channels/list

def test_channels_list_empty(setup_user):
    '''
    test when the user is not in any channels
    '''
    token = setup_user
    payload = {'token': token}
    response = requests.get(APP_URL + "/channels/list", params=payload)
    data = json.loads(response.text)
    assert data['channels'] == []

def test_channels_list_normal(setup_user):
    '''
    test when the user joins a channel
    '''
    token = setup_user
    payload = {'token': token}
    call_channels_create(token, "First Channel", True)
    response = requests.get(APP_URL + "/channels/list", params=payload)
    data = json.loads(response.text)
    assert data == {
        'channels':[
            {'channel_id': 1,
             'name':'First Channel'}
        ]
    }

def test_channels_list_multiple(setup_user):
    '''
    test when the user joins multiple channels
    '''
    token = setup_user
    payload = {'token': token}
    call_channels_create(token, "First Channel", True)
    call_channels_create(token, "Second Channel", True)
    response = requests.get(APP_URL + "/channels/list", params=payload)
    data = json.loads(response.text)
    #double check the dictionary format :(
    assert data == {
        'channels':[
            {'channel_id': 1,
             'name':'First Channel'},
            {'channel_id': 2,
             'name':'Second Channel'}
        ]
    }

def test_channels_list_invalid_token():
    '''
    test when the token is invalid
    '''
    payload = {'token': 'invalid token'}
    response = requests.get(APP_URL + "/channels/list", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

# Testing /channels/listall

def test_channels_listall(setup_user):
    '''
    Testing the channels listall function produces correct output
    '''

    token = setup_user

    # No channels added
    get_payload = {'token':token}

    response = requests.get(APP_URL + '/channels/listall', params=get_payload)
    data = json.loads(response.text)
    assert data == {'channels':[]}

    # Testing adding 1 channel
    payload = {'token':token, 'name':'My First Channel', 'is_public':False}
    requests.post(APP_URL + '/channels/create', json=payload)

    response = requests.get(APP_URL + '/channels/listall', params=get_payload)
    data = json.loads(response.text)
    assert data == {
        'channels': [
            {'channel_id': 1,
             'name': 'My First Channel'}
        ]
    }

    # Testing adding a second channel
    payload = {'token':token, 'name':'My 2nd Channel', 'is_public':True}
    requests.post(APP_URL + '/channels/create', json=payload)

    response = requests.get(APP_URL + '/channels/listall', params=get_payload)
    data = json.loads(response.text)
    assert data == {
        'channels': [
            {'channel_id': 1,
             'name': 'My First Channel'},
            {'channel_id': 2,
             'name': 'My 2nd Channel'}
        ]
    }

def test_channels_listall_fake_token(setup_user):
    '''
    Testing the channels/listall function with an invalid token
    '''
    _ = setup_user
    fake_token = ''

    payload = {'token':fake_token}
    response = requests.get(APP_URL + '/channels/listall', params=payload)

    assert response.status_code == 400 and 'invalid token' in response.text

# Testing /channels/create

def test_channels_create_public(setup_user):
    '''
    Testing creating a public channel
    '''
    token = setup_user

    payload = {"token": token, "name": 'My First Channel', "is_public": True}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)

    assert data['channel_id'] == 1

def test_channels_create_private(setup_user):
    '''
    Testing creating a private channel
    '''
    token = setup_user

    payload = {"token": token, "name": 'My First Channel', "is_public": False}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)

    assert data['channel_id'] == 1

def test_channels_create_public_long(setup_user):
    '''
    Testing creating a public channel with a name > 20 chrs long
    '''
    token = setup_user

    payload = {"token": token, "name": 'This Channel Name > 20 Chrs Longd', "is_public": True}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)

    assert response.status_code == 400 and 'Name is more than 20 characters long' in data['message']

def test_channels_create_private_long(setup_user):
    '''
    Tests a private channel with name that is more than 20 chrs long
    '''
    token = setup_user

    payload = {"token": token, "name": 'This Channel Name > 20 Chrs Longd', "is_public": False}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)

    assert response.status_code == 400 and 'Name is more than 20 characters long' in data['message']

def test_invalid_token_channels_create_public(setup_user):
    '''
    Testing attempting to create a public channel with an invalid token
    '''
    _ = setup_user
    fake_token = ''

    payload = {"token": fake_token, "name": 'My First Channel', "is_public": True}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)

    assert response.status_code == 400 and 'invalid token' in data['message']

def test_invalid_token_channels_create_private(setup_user):
    '''
    Testing attempting to create a public channel with an invalid token
    '''
    _ = setup_user
    fake_token = ''

    payload = {"token": fake_token, "name": 'My First Channel', "is_public": False}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)

    assert response.status_code == 400 and 'invalid token' in data['message']
