# pylint: disable=redefined-outer-name
'''
Tests channel routes at the HTTP level
'''

import json
from time import sleep
from datetime import datetime, timezone
import pytest
import requests
from http_test import APP_URL

### setup ###

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
    data = json.loads(response.text)
    return data["token"]

@pytest.fixture
def setup_user2():
    '''
    setup an user using register
    '''
    payload = {"email":"validemail1@gmail.com",
               "password": "123456",
               "name_first": "Hayden",
               "name_last": "Smith"}
    response = requests.post(APP_URL + "/auth/register", json=payload)
    data = json.loads(response.text)
    return data["token"]

def call_channels_create(token, name, is_public):
    '''
    Calls channels/create to create a channel for testing purposes
    '''
    payload = {"token": token, "name": name, "is_public": is_public}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)
    return data["channel_id"]

def call_standup_start(token, channel_id, length):
    '''
    Call standup_start to start the standup
    '''
    payload = {"token": token, "channel_id": channel_id, "length": length}
    response = requests.post(APP_URL + "/standup/start", json=payload)
    data = json.loads(response.text)
    return data["time_finish"]

def test_standup_start_invalid_channel(setup_user):
    '''
    test for error from invalid channel id
    '''
    token = setup_user
    payload = {"token": token, "channel_id": -1, "length": 1}
    response = requests.post(APP_URL + "/standup/start", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]
    sleep(2)

def test_standup_start_user_not_member(setup_user, setup_user2):
    '''
    test for error from user not in standup channel
    '''
    token = setup_user
    token2 = setup_user2
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token2, "channel_id": channel_id, "length": 1}
    response = requests.post(APP_URL + "/standup/start", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User not in the channel" in data["message"]
    sleep(2)

def test_standup_start_normal(setup_user):
    '''
    test for a normal case
    '''
    token = setup_user
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token, "channel_id": channel_id, "length": 1}
    start_time = datetime.utcnow()
    start_time = start_time.replace(tzinfo=timezone.utc).timestamp()
    response = requests.post(APP_URL + "/standup/start", json=payload)
    data = json.loads(response.text)
    assert data["time_finish"] > start_time
    sleep(2)

def test_standup_active_invalid_channel(setup_user):
    '''
    test for when the channel id for standup is invalid
    '''
    token = setup_user
    payload = {"token": token, "channel_id": -1}
    response = requests.get(APP_URL + "/standup/active", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_standup_active_user_not_member(setup_user, setup_user2):
    '''
    test for when the user is not a member of the channel
    '''
    token = setup_user
    token1 = setup_user2
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token1, "channel_id": channel_id}
    response = requests.get(APP_URL + "/standup/active", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User not in the channel" in data["message"]

def test_standup_active_not_active(setup_user):
    '''
    test for when the standup in the channel is not active
    '''
    token = setup_user
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/standup/active", params=payload)
    data = json.loads(response.text)
    assert data["is_active"] is False

def test_standup_active_isactive(setup_user):
    '''
    test for when the standup in the channel is active
    '''
    token = setup_user
    channel_id = call_channels_create(token, "standup", True)
    call_standup_start(token, channel_id, 1)
    payload = {"token": token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/standup/active", params=payload)
    data = json.loads(response.text)
    assert data["is_active"] is True
    sleep(2)

def test_standup_send_invalid_channel(setup_user):
    '''
    test for when the channel id is invalid
    '''
    token = setup_user
    payload = {"token": token, "channel_id": -1, "message": "message"}
    response = requests.post(APP_URL + "/standup/send", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_standup_send_not_member(setup_user, setup_user2):
    '''
    test for when the user is not a member of the channel
    '''
    token = setup_user
    token2 = setup_user2
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token2, "channel_id": channel_id, "message": "message"}
    response = requests.post(APP_URL + "/standup/send", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User not in the channel" in data["message"]

def test_standup_send_message_long(setup_user):
    '''
    test for when the message is greater than 1000 characters
    '''
    token = setup_user
    message = 'a' * 1001
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token, "channel_id": channel_id, "message": message}
    response = requests.post(APP_URL + "/standup/send", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and \
        "Message is greater than 1000 characters" in data["message"]

def test_standup_send_standup_not_active(setup_user):
    '''
    test for when theres no active standup in the channel
    '''
    token = setup_user
    channel_id = call_channels_create(token, "standup", True)
    payload = {"token": token, "channel_id": channel_id, "message": "message"}
    response = requests.post(APP_URL + "/standup/send", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and \
        "An active standup is not currently running in this channel" in data["message"]

def test_standup_send_normal(setup_user):
    '''
    test for a normal case of standup_send
    '''
    token = setup_user
    channel_id = call_channels_create(token, "standup", True)
    call_standup_start(token, channel_id, 1)
    payload = {"token": token, "channel_id": channel_id, "message": "message"}
    response = requests.post(APP_URL + "/standup/send", json=payload)
    data = json.loads(response.text)
    assert data == {}
    sleep(2)
