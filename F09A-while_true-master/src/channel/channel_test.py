# pylint: disable=redefined-outer-name,not-an-iterable
'''
Tests the backend functionality of the channel routes
'''

from time import time
import pytest
from channel import channel_invite, channel_details, channel_messages, channel_leave, \
                    channel_join, channel_addowner, channel_removeowner
from auth import auth_register, auth_logout
from channels import channels_create
from message import message_send, message_sendlater
from workspace_reset import workspace_reset
from error import InputError, AccessError


### helper functions ###

def is_details_valid(data):
    ''' Checks if return values from channel_details is valid '''
    return isinstance(data, dict) \
           and "name" in data \
           and "owner_members" in data \
           and "all_members" in data \
           and isinstance(data["name"], str) \
           and isinstance(data["owner_members"], list) \
           and (all(isinstance(x, dict) for x in data["owner_members"])) \
           and isinstance(data["all_members"], list) \
           and (all(isinstance(x, dict) for x in data["all_members"]))

def is_messages_valid(data):
    ''' Checks if return values from channel_messages is valid '''
    return isinstance(data, dict) \
           and "messages" in data \
           and "start" in data \
           and "end" in data \
           and isinstance(data["messages"], list) \
           and isinstance(data["start"], int) \
           and isinstance(data["end"], int)

def create_messages(channel_id, token, msg, count, seconds_later):
    ''' Creates messages of the string "msg" for the "count" times in the channel
    based on it's id. If seconds_later is greater than 0, the message will be sent
    later '''
    for _ in range(count):
        if seconds_later > 0:
            message_sendlater(token, channel_id, msg, int(time()) + seconds_later)
        else:
            message_send(token, channel_id, msg)


### setup ###

@pytest.fixture(autouse=True)
def call_workspace_reset():
    ''' Automatic fixture to reset state between tests '''
    workspace_reset()

@pytest.fixture
def setup_user_1():
    ''' Setups a user and returns a dictionary of the user's ID and token '''
    data = auth_register("validemail@gmail.com", "validpassword1", "John", "Citizen")
    return {"u_id": data["u_id"], "token": data["token"]}

@pytest.fixture
def setup_user_2():
    ''' Setups a user and returns a dictionary of the user's ID and token '''
    data = auth_register("email@gmail.com", "validpassword2", "Jane", "Citizen")
    return {"u_id": data["u_id"], "token": data["token"]}

### test channel_invite ###

# pass cases #

def test_channel_invite_normal(setup_user_1, setup_user_2):
    ''' Tests if a valid channel/invite case works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]

    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    assert channel_invite(user_1_token, channel_id, user_2_id) == {}
    assert any(item["u_id"] == user_2_id \
            for item in channel_details(user_1_token, channel_id)["all_members"])

# fail cases #

def test_channel_invite_invalid_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an invalid token '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_invite("12345", channel_id, user_2_id)

def test_channel_invite_logged_out_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for a logged out token '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    auth_logout(user_1_token)

    with pytest.raises(AccessError):
        channel_invite(user_1_token, channel_id, user_2_id)

def test_channel_invite_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for an invalid channel id '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(user_1_token, channel_id + 1, user_2_id)

def test_channel_invite_invalid_user_id(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for an invalid user id '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(user_1_token, channel_id, user_2_id + 1)

def test_channel_invite_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_invite(user_2_token, channel_id, user_2_id)

def test_channel_invite_inviting_twice(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised when a user is invited twice '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    assert channel_invite(user_1_token, channel_id, user_2_id) == {}
    with pytest.raises(InputError):
        # Assuming inviting the same user twice will cause an InputError
        channel_invite(user_1_token, channel_id, user_2_id)

### test channel_details ###

# pass cases #

def test_channel_details_normal(setup_user_1):
    ''' Tests if a valid channel/details case works as intended '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    assert is_details_valid(channel_details(token, channel_id))

# fail cases #

def test_channel_details_invalid_token(setup_user_1):
    ''' Tests if an AccessError is raised for an invalid token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_details("12345", channel_id)

def test_channel_details_logged_out_token(setup_user_1):
    ''' Tests if an AccessError is raised for a logged out token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(AccessError):
        channel_details(token, channel_id)

def test_channel_details_invalid_channel_id(setup_user_1):
    ''' Tests if an InputError is raised for an invalid channel id '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_details(token, channel_id + 1)

def test_channel_details_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_details(user_2_token, channel_id)

### test channel_messages ###

# pass cases #

def test_channel_messages_normal(setup_user_1):
    ''' Tests if a valid channel/messages case works as intended '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    create_messages(channel_id, token, "hi", 1, 0)

    assert is_messages_valid(channel_messages(token, channel_id, 0))

def test_channel_messages_contains_messages(setup_user_1):
    ''' Tests if channel contains messages when messages are created '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    create_messages(channel_id, token, "hello", 75, 0)

    messages = channel_messages(token, channel_id, 5)
    assert messages["end"] == 55
    assert len(messages["messages"]) > 0

def test_channel_messages_contains_no_messages(setup_user_1):
    ''' Tests if channel contains no messages when created '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    messages = channel_messages(token, channel_id, 0)
    assert messages["end"] == -1
    assert len(messages["messages"]) == 0

def test_channel_messages_least_recent(setup_user_1):
    ''' Tests if channel messages contain the least recent messages '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    create_messages(channel_id, token, "hello", 75, 0)

    messages = channel_messages(token, channel_id, 26)
    assert messages["end"] == -1

def test_channel_messages_sendlater(setup_user_1):
    ''' Tests if channel messages do not contain messages that are sent later '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    create_messages(channel_id, token, "first msg", 1, 0)

    # Send messages 15 seconds later
    create_messages(channel_id, token, "hello", 5, 15)

    messages = channel_messages(token, channel_id, 0)
    assert len(messages["messages"]) == 1
    assert messages["end"] == -1

# fail cases #

def test_channel_messages_invalid_token(setup_user_1):
    ''' Tests if an AccessError is raised for an invalid token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_messages("12345", channel_id, 0)

def test_channel_messages_logged_out_token(setup_user_1):
    ''' Tests if an AccessError is raised for a logged out token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(AccessError):
        channel_messages(token, channel_id, 0)

def test_channel_messages_invalid_channel_id(setup_user_1):
    ''' Tests if an InputError is raised for an invalid channel id '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_messages(token, channel_id + 1, 0)

def test_channel_messages_start_greater(setup_user_1):
    ''' Tests if an InputError is raised for start being greater than the
    ammount of messages in a channel '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_messages(token, channel_id, 5000)

def test_channel_messages_negative_start(setup_user_1):
    ''' Tests if an InputError is raised for a negative start '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_messages(token, channel_id, -1) # Assuming start cannot be less than 0

def test_channel_messages_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_messages(user_2_token, channel_id, 0)

### test channel_leave ###

# pass cases #

def test_channel_leave_normal(setup_user_1, setup_user_2):
    ''' Tests if a valid channel/leave case works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]

    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    assert channel_leave(user_2_token, channel_id) == {}

# fail cases #

def test_channel_leave_invalid_token(setup_user_1):
    ''' Tests if an AccessError is raised for an invalid token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_leave("12345", channel_id)

def test_channel_leave_logged_out_token(setup_user_1):
    ''' Tests if an AccessError is raised for a logged out token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(AccessError):
        channel_leave(token, channel_id)

def test_channel_leave_invalid_channel_id(setup_user_1):
    ''' Tests if an InputError is raised for an invalid channel id '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_leave(token, channel_id + 1)

def test_channel_leave_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_leave(user_2_token, channel_id)

def test_channel_leave_twice(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised when a user tries to leave twice '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]

    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    assert channel_leave(user_2_token, channel_id) == {}
    with pytest.raises(AccessError):
        channel_leave(user_2_token, channel_id)

def test_channel_leave_owner(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised when an owner tries to leave '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]

    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)
    channel_addowner(user_1_token, channel_id, user_2_id)

    with pytest.raises(InputError):
        channel_leave(user_2_token, channel_id)

### test channel_join ###

# pass cases #

def test_channel_join_normal(setup_user_1, setup_user_2):
    ''' Tests if a valid channel/join case works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    assert channel_join(user_2_token, channel_id) == {}

# fail cases #

def test_channel_join_invalid_token(setup_user_1):
    ''' Tests if an AccessError is raised for an invalid token '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_join("12345", channel_id)

def test_channel_join_logged_out_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for a logged out token '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    auth_logout(user_2_token)

    with pytest.raises(AccessError):
        channel_join(user_2_token, channel_id)

def test_channel_join_invalid_channel_id(setup_user_1):
    ''' Tests if an InputError is raised for an invalid channel id '''
    token = setup_user_1["token"]
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_join(token, channel_id + 1)

def test_channel_join_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", False)["channel_id"]

    with pytest.raises(AccessError):
        channel_join(user_2_token, channel_id)

def test_channel_join_twice(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised when a user is invited twice '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    assert channel_join(user_2_token, channel_id) == {}
    with pytest.raises(InputError):
        # Assuming an InputError is raised when attempting to join twice
        channel_join(user_2_token, channel_id)

### test channel_addowner ###

# pass cases #

def test_channel_addowner_normal(setup_user_1, setup_user_2):
    ''' Tests if a valid channel/addowner case works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    assert channel_addowner(user_1_token, channel_id, user_2_id) == {}

# fail cases #

def test_channel_addowner_invalid_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an invalid token '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    with pytest.raises(AccessError):
        channel_addowner("12345", channel_id, user_2_id)

def test_channel_addowner_logged_out_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for a logged out token '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)
    auth_logout(user_1_token)

    with pytest.raises(AccessError):
        channel_addowner(user_1_token, channel_id, user_2_id)

def test_channel_addowner_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for an invalid channel id '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    with pytest.raises(InputError):
        channel_addowner(user_1_token, channel_id + 1, user_2_id)

def test_channel_addowner_invalid_user_id(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for an invalid user id '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    with pytest.raises(InputError):
        channel_addowner(user_1_token, channel_id, user_2_id + 1)

def test_channel_addowner_already_owner(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for user being added as an owner
    despite being one already '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    channel_addowner(user_1_token, channel_id, user_2_id)
    with pytest.raises(InputError):
        channel_addowner(user_1_token, channel_id, user_2_id)

def test_channel_addowner_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    with pytest.raises(AccessError):
        channel_addowner(user_2_token, channel_id, user_2_id)

### test_channel_removeowner ###

# pass cases #

def test_channel_removeowner_normal(setup_user_1, setup_user_2):
    ''' Tests if a valid channel/removeowner case works as intended '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)
    channel_addowner(user_1_token, channel_id, user_2_id)

    assert channel_removeowner(user_1_token, channel_id, user_2_id) == {}

# fail cases #

def test_channel_removeowner_invalid_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an invalid token '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)
    channel_addowner(user_1_token, channel_id, user_2_id)

    with pytest.raises(AccessError):
        channel_removeowner("12345", channel_id, user_2_id)

def test_channel_removeowner_logged_out_token(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for a logged out token '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)
    channel_addowner(user_1_token, channel_id, user_2_id)
    auth_logout(user_1_token)

    with pytest.raises(AccessError):
        channel_removeowner(user_1_token, channel_id, user_2_id)

def test_channel_removeowner_invalid_channel_id(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for an invalid channel id '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)
    channel_addowner(user_1_token, channel_id, user_2_id)

    with pytest.raises(InputError):
        channel_removeowner(user_1_token, channel_id + 1, user_2_id)

def test_channel_removeowner_not_in_channel(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised when a user is being removed as an
    owner despite not being in the channel '''
    user_1_token = setup_user_1["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_removeowner(user_1_token, channel_id, user_2_id)

def test_channel_removeowner_not_an_owner(setup_user_1, setup_user_2):
    ''' Tests if an InputError is raised for user being removed as an owner
    despite not being one '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_2_id = setup_user_2["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    with pytest.raises(InputError):
        channel_removeowner(user_1_token, channel_id, user_2_id)

def test_channel_removeowner_unauthorised(setup_user_1, setup_user_2):
    ''' Tests if an AccessError is raised for an unauthorised user '''
    user_1_token = setup_user_1["token"]
    user_2_token = setup_user_2["token"]
    user_1_id = setup_user_1["u_id"]
    channel_id = channels_create(user_1_token, "Chan1", True)["channel_id"]
    channel_join(user_2_token, channel_id)

    with pytest.raises(AccessError):
        channel_removeowner(user_2_token, channel_id, user_1_id)
