# pylint: disable=redefined-outer-name
'''
Tests channel routes at the HTTP level
'''

import json
import pytest
import requests
from http_test import APP_URL

### setup ###

@pytest.fixture(autouse=True)
def call_workspace_reset():
    ''' Automatic fixture to reset state between tests '''
    requests.post(APP_URL + "/workspace/reset")

@pytest.fixture
def setup_user_1():
    ''' Setups a user and returns a dictionary of the user's ID and token '''
    payload = {"email": "johncitizen@hotmail.com",
               "password": "abcdef1",
               "name_first": "John",
               "name_last": "Citizen"}
    response = requests.post(APP_URL + "/auth/register", json=payload)
    data = json.loads(response.text)
    return {"u_id": data["u_id"], "token": data["token"]}

@pytest.fixture
def setup_user_2():
    ''' Setups a user and returns a dictionary of the user's ID and token '''
    payload = {"email": "janecitizen@hotmail.com",
               "password": "abcdef1",
               "name_first": "Jane",
               "name_last": "Citizen"}
    response = requests.post(APP_URL + "/auth/register", json=payload)
    data = json.loads(response.text)
    return {"u_id": data["u_id"], "token": data["token"]}

@pytest.fixture
def setup_user_3():
    ''' Setups a user and returns a dictionary of the user's ID and token '''
    payload = {"email": "jackcitizen@hotmail.com",
               "password": "abcdef1",
               "name_first": "Jack",
               "name_last": "Citizen"}
    response = requests.post(APP_URL + "/auth/register", json=payload)
    data = json.loads(response.text)
    return {"u_id": data["u_id"], "token": data["token"]}

def call_channels_create(token, name, is_public):
    ''' Calls channels/create to create a channel for testing purposes '''
    payload = {"token": token, "name": name, "is_public": is_public}
    response = requests.post(APP_URL + "/channels/create", json=payload)
    data = json.loads(response.text)
    return data["channel_id"]

def call_message_send(token, channel_id, message):
    ''' Calls message/send to create messages on a channel for testing purposes '''
    payload = {"token": token, "channel_id": channel_id, "message": message}
    response = requests.post(APP_URL + "/message/send", json=payload)
    data = json.loads(response.text)
    return data["message_id"]

def call_channel_invite(token, channel_id, u_id):
    ''' Calls channel/invite to invite a user to a channel for testing purposes '''
    payload = {"token": token, "channel_id": channel_id, "u_id": u_id}
    requests.post(APP_URL + "/channel/invite", json=payload)

def call_channel_addowner(token, channel_id, u_id):
    ''' Calls channel/addowner to make a user a channel owner for testing purposes '''
    payload = {"token": token, "channel_id": channel_id, "u_id": u_id}
    requests.post(APP_URL + "/channel/addowner", json=payload)

### Tests ###

# channel/invite Tests

def test_channel_invite_normal(setup_user_1, setup_user_2):
    ''' Test if a valid channel/invite route call works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/invite
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/invite", json=payload)
    data = json.loads(response.text)
    assert data == {}

    # Call channel/details to verify user 2 is in the channel
    payload = {"token": user_1_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert any(item["u_id"] == user_2_id for item in data["all_members"])

def test_channel_invite_invalid_token(setup_user_1, setup_user_2):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/invite with invalid token
    payload = {"token": "12345", "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/invite", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_invite_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]

    # Call channel/invite with invalid channel id
    payload = {"token": user_1_token, "channel_id": 1, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/invite", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_invite_invalid_user_id(setup_user_1, setup_user_2):
    ''' Tests if InputError of "invalid user ID" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/invite with invalid user id
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id + 1}
    response = requests.post(APP_URL + "/channel/invite", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid user ID" in data["message"]

def test_channel_invite_unauth(setup_user_1, setup_user_2, setup_user_3):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_3_id = setup_user_3["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/invite with a user token that is not in the channel
    payload = {"token": user_2_token, "channel_id": channel_id, "u_id": user_3_id}
    response = requests.post(APP_URL + "/channel/invite", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

def test_channel_invite_invite_twice(setup_user_1, setup_user_2):
    ''' Tests if InputError of "User is already in the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/invite
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    requests.post(APP_URL + "/channel/invite", json=payload)

    # Call channel/invite again
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/invite", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User is already in the channel" in data["message"]

# channel/details Tests

def test_channel_details_normal(setup_user_1):
    ''' Test if a valid channel/details route call works as intended '''
    user_token = setup_user_1["token"]
    user_id = setup_user_1["u_id"]
    channel_id = call_channels_create(user_token, "channel 1", True)

    # Call channel/details
    payload = {"token": user_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)

    # Sanity check for the data returned
    assert data == {"name": "channel 1",
                    "owner_members": [
                        {
                            "u_id": user_id,
                            "name_first": "John",
                            "name_last": "Citizen",
                            "profile_img_url": "https://iupac.org/wp-content/uploads/2018/05/default-avatar.png"
                        }
                    ],
                    "all_members": [
                        {
                            "u_id": user_id,
                            "name_first": "John",
                            "name_last": "Citizen",
                            "profile_img_url": "https://iupac.org/wp-content/uploads/2018/05/default-avatar.png"
                        }
                    ]
                   }

def test_channel_details_invalid_token(setup_user_1):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_token = setup_user_1["token"]
    channel_id = call_channels_create(user_token, "channel 1", True)

    # Call channel/details with an invalid token
    payload = {"token": "12345", "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_details_invalid_channel_id(setup_user_1):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_token = setup_user_1["token"]

    # Call channel/details with an invalid channel id
    payload = {"token": user_token, "channel_id": 1}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_details_unauth(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/details with a user who isn't in the channel
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

# channel/messages Tests

def test_channel_messages_normal(setup_user_1):
    ''' Test if a valid channel/messages route call works as intended '''
    user_token = setup_user_1["token"]
    channel_id = call_channels_create(user_token, "channel 1", True)
    call_message_send(user_token, channel_id, "Hello")

    # Call channel/messages
    payload = {"token": user_token, "channel_id": channel_id, "start": 0}
    response = requests.get(APP_URL + "/channel/messages", params=payload)
    data = json.loads(response.text)
    assert len(data["messages"]) == 1 and \
            data["messages"][0]["message"] == "Hello" and \
            data["start"] == 0 and \
            data["end"] == -1

def test_channel_messages_invalid_token(setup_user_1):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_token = setup_user_1["token"]
    channel_id = call_channels_create(user_token, "channel 1", True)

    # Call channel/messages with an invalid token
    payload = {"token": "12345", "channel_id": channel_id, "start": 0}
    response = requests.get(APP_URL + "/channel/messages", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_messages_invalid_channel_id(setup_user_1):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_token = setup_user_1["token"]

    # Call channel/messages with an invalid channel id
    payload = {"token": user_token, "channel_id": 1, "start": 0}
    response = requests.get(APP_URL + "/channel/messages", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_messages_unauth(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/messages with a user who isn't in the channel
    payload = {"token": user_2_token, "channel_id": channel_id, "start": 0}
    response = requests.get(APP_URL + "/channel/messages", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

def test_channel_messages_start_greater(setup_user_1):
    '''
    Tests if InputError of "Start is greater than
    or equal to the total number of messages" occurs
    '''
    user_token = setup_user_1["token"]
    channel_id = call_channels_create(user_token, "channel 1", True)
    call_message_send(user_token, channel_id, "Hello")

    # Call channel/messages with a start position greater
    # than the total number of messages
    payload = {"token": user_token, "channel_id": channel_id, "start": 2}
    response = requests.get(APP_URL + "/channel/messages", params=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Start is not valid" \
            in data["message"]

# channel/leave Tests

def test_channel_leave_normal(setup_user_1, setup_user_2):
    ''' Test if a valid channel/leave route call works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]

    # Make a channel using user 1 and add user 2 to the channel
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/leave
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/leave", json=payload)
    data = json.loads(response.text)
    assert data == {}

    # Call channel/details to verify user 2 is not in the channel
    payload = {"token": user_1_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert not any(item["u_id"] == user_2_id for item in data["all_members"])

def test_channel_leave_invalid_token(setup_user_1):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_token = setup_user_1["token"]
    channel_id = call_channels_create(user_token, "channel 1", True)

    # Call channel/leave with an invalid token
    payload = {"token": "12345", "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/leave", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_leave_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]

    # Make a channel using user 1 and add user 2 to the channel
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/leave with an invalid channel id
    payload = {"token": user_2_token, "channel_id": channel_id + 1}
    response = requests.post(APP_URL + "/channel/leave", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_leave_unauth(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/leave with a user not in the channel
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/leave", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

def test_channel_leave_owner_leave(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Owners cannot leave the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]

    # Make a channel using user 1 and add user 2 to the channel and make it
    # an owner
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)
    call_channel_addowner(user_1_token, channel_id, user_2_id)

    # Call channel/leave with on a user who is an owner
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/leave", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Owners cannot leave the channel" in data["message"]

# channel/join Tests

def test_channel_join_normal(setup_user_1, setup_user_2):
    ''' Test if a valid channel/join route call works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/join
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/join", json=payload)
    data = json.loads(response.text)
    assert data == {}

    # Call channel/details to verify user 2 is not in the channel
    payload = {"token": user_1_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert any(item["u_id"] == user_2_id for item in data["all_members"])

def test_channel_join_invalid_token(setup_user_1):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_token = setup_user_1["token"]
    channel_id = call_channels_create(user_token, "channel 1", True)

    # Call channel/join with an invalid token
    payload = {"token": "12345", "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/join", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_join_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/join with an invalid channel id
    payload = {"token": user_2_token, "channel_id": channel_id + 1}
    response = requests.post(APP_URL + "/channel/join", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_join_unauth(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = call_channels_create(user_1_token, "channel 1", False)

    # Call channel/join on a private channel using a user without owner permissions
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/join", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

def test_channel_join_join_twice(setup_user_1, setup_user_2):
    ''' Tests if InputError of "User is already in the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/join
    payload = {"token": user_2_token, "channel_id": channel_id}
    requests.post(APP_URL + "/channel/join", json=payload)

    # Call channel/join again
    payload = {"token": user_2_token, "channel_id": channel_id}
    response = requests.post(APP_URL + "/channel/join", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User is already in the channel" in data["message"]

# channel/addowner Tests

def test_channel_addowner_normal(setup_user_1, setup_user_2):
    ''' Test if a valid channel/addowner route call works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/addowner
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/addowner", json=payload)
    data = json.loads(response.text)
    assert data == {}

    # Call channel/details to verify user 2 is an owner
    payload = {"token": user_1_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert any(item["u_id"] == user_2_id for item in data["owner_members"])

def test_channel_addowner_invalid_token(setup_user_1, setup_user_2):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/addowner with an invalid token
    payload = {"token": "12345", "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/addowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_addowner_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/addowner with an invalid channel id
    payload = {"token": user_1_token, "channel_id": channel_id + 1, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/addowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_addowner_user_not_in_channel(setup_user_1, setup_user_2):
    ''' Tests if InputError of "User is not in the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/addowner on a user who isn't in the channel
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/addowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User is not in the channel" in data["message"]

def test_channel_addowner_unauth(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/addowner using a user who isn't an owner to add an owner
    payload = {"token": user_2_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/addowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

def test_channel_addowner_already_owner(setup_user_1, setup_user_2):
    ''' Tests if InputError of "User is already an owner of the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/addowner
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    requests.post(APP_URL + "/channel/addowner", json=payload)

    # Call channel/addowner on the same user
    payload = {"token": user_2_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/addowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and \
            "User is already an owner of the channel" in data["message"]

# channel/removeowner Tests

def test_channel_removeowner_normal(setup_user_1, setup_user_2):
    ''' Test if a valid channel/removeowner route call works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)
    call_channel_addowner(user_1_token, channel_id, user_2_id)

    # Call channel/removeowner
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/removeowner", json=payload)
    data = json.loads(response.text)
    assert data == {}

    # Call channel/removeowner to verify user 2 is not an owner
    payload = {"token": user_1_token, "channel_id": channel_id}
    response = requests.get(APP_URL + "/channel/details", params=payload)
    data = json.loads(response.text)
    assert user_2_id not in data["owner_members"]

def test_channel_removeowner_invalid_token(setup_user_1, setup_user_2):
    ''' Tests if AccessError of "invalid token" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)
    call_channel_addowner(user_1_token, channel_id, user_2_id)

    # Call channel/removeowner with an invalid token
    payload = {"token": "12345", "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/removeowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid token" in data["message"]

def test_channel_removeowner_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if InputError of "invalid channel ID" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)
    call_channel_addowner(user_1_token, channel_id, user_2_id)

    # Call channel/removeowner with an invalid channel id
    payload = {"token": user_1_token, "channel_id": channel_id + 1, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/removeowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "invalid channel ID" in data["message"]

def test_channel_removeowner_user_not_in_channel(setup_user_1, setup_user_2):
    ''' Tests if InputError of "User is not in the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)

    # Call channel/removeowner on a user who isn't in the channel
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/removeowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "User is not in the channel" in data["message"]

def test_channel_removeowner_unauth(setup_user_1, setup_user_2):
    ''' Tests if InputError of "Unauthorised User" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/removeowner using a user who isn't an owner to add an owner
    payload = {"token": user_2_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/removeowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and "Unauthorised User" in data["message"]

def test_channel_removeowner_not_an_owner(setup_user_1, setup_user_2):
    ''' Tests if InputError of "User is not an owner of the channel" occurs '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = call_channels_create(user_1_token, "channel 1", True)
    call_channel_invite(user_1_token, channel_id, user_2_id)

    # Call channel/removeowner with a user who isn't an owner
    payload = {"token": user_1_token, "channel_id": channel_id, "u_id": user_2_id}
    response = requests.post(APP_URL + "/channel/removeowner", json=payload)
    data = json.loads(response.text)
    assert response.status_code == 400 and \
            "User is not an owner of the channel" in data["message"]
