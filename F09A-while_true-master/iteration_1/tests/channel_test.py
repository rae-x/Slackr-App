import pytest
from channel import channel_invite, channel_details, channel_messages, channel_leave, \
                    channel_join, channel_addowner, channel_removeowner
from auth import auth_register, auth_logout
from channels import channels_create
from message import message_send
from error import InputError, AccessError


### helper functions ###

def is_details_valid(data):
    return type(data) is dict \
           and "name" in data \
           and "owner_members" in data \
           and "all_members" in data \
           and type(data["name"]) is str \
           and type(data["owner_members"]) is list \
           and (all(isinstance(x, dict) for x in data["owner_members"])) \
           and type(data["all_members"]) is list \
           and (all(isinstance(x, dict) for x in data["all_members"]))

def is_messages_valid(data):
    return type(data) is dict \
           and "messages" in data \
           and "start" in data \
           and "end" in data \
           and type(data["messages"]) is list \
           and (all(isinstance(x, dict) for x in data["messages"])) \
           and type(data["start"]) is int \
           and type(data["end"]) is int

### setup ###

@pytest.fixture
def setup_user_1():
    data = auth_register("validemail@gmail.com", "validpassword1", "John", "Citizen")
    return (data["u_id"], data["token"])

@pytest.fixture
def setup_user_2():
    data = auth_register("email@gmail.com", "validpassword2", "Jane", "Citizen")
    return (data["u_id"], data["token"])

### test channel_invite ###

# pass cases #

def test_channel_invite_normal(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2

    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]
    assert channel_invite(token_1, channel_id, u_id_2) == {}

# fail cases #

def test_channel_invite_invalid_channel(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(token_1, channel_id + 1, u_id_2)

def test_channel_invite_negative_channel_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2

    with pytest.raises(InputError):
        channel_invite(token_1, -1, u_id_2)     # Assuming negative channel ids are invalid

def test_channel_invite_invalid_user_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(token_1, channel_id, u_id_2 + 1)

def test_channel_invite_negative_user_id(setup_user_1):
    u_id_1, token_1 = setup_user_1
    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_invite(token_1, channel_id, -1)   # Assuming negative user ids are invalid

def test_channel_invite_unauthorised(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]
    auth_logout(token_1)

    with pytest.raises(AccessError):
        channel_invite(token_1, channel_id, u_id_2)

def test_channel_invite_inviting_twice(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]

    assert channel_invite(token_1, channel_id, u_id_2) == {}
    with pytest.raises(AccessError):
        channel_invite(token_1, channel_id, u_id_2) # Assuming inviting the same user twice will cause an AccessError

### test channel_details ###

# pass cases #

def test_channel_details_normal(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    assert is_details_valid(channel_details(token, channel_id))

# fail cases #

def test_channel_details_invalid_channel_id(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_details(token, channel_id + 1)

def test_channel_details_negative_channel_id(setup_user_1):
    u_id, token = setup_user_1

    with pytest.raises(InputError):
        channel_details(token, -1)  # Assuming negative channel ids are invalid

def test_channel_details_unauthorised(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(AccessError):
        channel_details(token, channel_id)

def test_channel_details_invalid_channel_unauth(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)
    
    with pytest.raises(InputError):
        channel_details(token, channel_id + 1)

### test channel_messages ###

# pass cases #

def test_channel_messages_normal(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    
    assert is_messages_valid(channel_messages(token, channel_id, 0))

def test_channel_messages_contains_messages(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    for i in range(75):
        message_send(token, channel_id, "hello")

    messages = channel_messages(token, channel_id, 5)
    assert messages["end"] == 55
    assert len(messages["messages"]) > 0

def test_channel_messages_contains_no_messages(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    messages = channel_messages(token, channel_id, 0)
    assert messages["end"] == -1
    assert len(messages["messages"]) == 0

def test_channel_messages_least_recent(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    for i in range(75):
        message_send(token, channel_id, "hello")
    
    messages = channel_messages(token, channel_id, 26)
    assert messages["end"] == -1

# fail cases #

def test_channel_messages_invalid_channel_id(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_messages(token, channel_id + 1, 0)

def test_channel_messages_negative_channel_id(setup_user_1):
    u_id, token = setup_user_1
    
    with pytest.raises(InputError):
        channel_messages(token, -1, 0)  # Assuming negative channel ids are invalid

def test_channel_messages_start_greater(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_messages(token, channel_id, 5000)

def test_channel_messages_negative_start(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_messages(token, channel_id, -1) # Assuming start cannot be less than 0

def test_channel_messages_unauthorised(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(AccessError):
        channel_messages(token, channel_id, 0)

def test_channel_messages_invalid_channel_unauth(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(InputError):
        channel_messages(token, channel_id + 1, 0)

### test channel_leave ###

# pass cases #

def test_channel_leave_normal(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    assert channel_leave(token, channel_id) == {}

# fail cases #

def test_channel_leave_invalid_channel_id(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_leave(token, channel_id + 1)

def test_channel_leave_negative_channel_id(setup_user_1):
    u_id, token = setup_user_1

    with pytest.raises(InputError):
        channel_leave(token, -1)    # Assuming negative channel ids are invalid

def test_channel_leave_unauthorised(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(AccessError):
        channel_leave(token, channel_id)

def test_channel_leave_invalid_channel_unauth(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]
    auth_logout(token)

    with pytest.raises(InputError):
        channel_leave(token, channel_id + 1)

def test_channel_leave_twice(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    assert channel_leave(token, channel_id) == {}
    with pytest.raises(AccessError):
        channel_leave(token, channel_id)

### test channel_join ###

# pass cases #

def test_channel_join_normal(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", True)["channel_id"]

    assert channel_join(token_2, channel_id) == {}

# fail cases #

def test_channel_join_invalid_channel_id(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_join(token, channel_id + 1)

def test_channel_join_negative_channel_id(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", True)["channel_id"]

    with pytest.raises(InputError):
        channel_join(token, -1) # Assuming negative channel ids are invalid

def test_channel_join_unauthorised(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    with pytest.raises(AccessError):
        channel_join(token_2, channel_id)

def test_channel_join_twice(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    assert channel_join(token_2, channel_id) == {}
    with pytest.raises(AccessError):    # Assuming an AccessError is raised when attempting to join twice
        channel_join(token_2, channel_id)

### test channel_addowner ###

# pass cases #

def test_channel_addowner_normal(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    assert channel_addowner(token_1, channel_id, u_id_2) == {}

# fail cases #

def test_channel_addowner_invalid_channel_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    with pytest.raises(InputError):
        channel_addowner(token_1, channel_id + 1, u_id_2)

def test_channel_addowner_negative_channel_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2

    with pytest.raises(InputError):
        channel_addowner(token_1, -1, u_id_2)   # Assuming negative channel ids are invalid

def test_channel_addowner_invalid_user_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    with pytest.raises(InputError):
        channel_addowner(token_1, channel_id, u_id_2 + 1)

def test_channel_addowner_negative_user_id(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", False)["channel_id"]

    with pytest.raises(InputError):
        channel_addowner(token, channel_id, -1)  # Assuming negative user ids are invalid

def test_channel_addowner_already_owner(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    channel_addowner(token_1, channel_id, u_id_2)
    with pytest.raises(InputError):
        channel_addowner(token_1, channel_id, u_id_2)

def test_channel_addowner_unauthorised(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]
    auth_logout(token_1)

    with pytest.raises(AccessError):
        channel_addowner(token_1, channel_id, u_id_2)

### test_channel_removeowner ###

# pass cases #

def test_channel_removeowner_normal(setup_user_1):
    u_id, token = setup_user_1
    channel_id = channels_create(token, "Chan1", False)["channel_id"]

    assert channel_removeowner(token, channel_id, u_id) == {}

# fail cases #

def test_channel_removeowner_invalid_channel_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]

    with pytest.raises(InputError):
        channel_removeowner(token_1, channel_id + 1, u_id_2)

def test_channel_removeowner_negative_channel_id(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2

    with pytest.raises(InputError):
        channel_removeowner(token_1, -1, u_id_2)    # Assuming negative channel ids are invalid

def test_channel_removeowner_not_an_owner(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]
    channel_join(token_2, channel_id)

    with pytest.raises(InputError):
        channel_removeowner(token_1, channel_id, u_id_2)

def test_channel_removeowner_unauthorised(setup_user_1, setup_user_2):
    u_id_1, token_1 = setup_user_1
    u_id_2, token_2 = setup_user_2
    channel_id = channels_create(token_1, "Chan1", False)["channel_id"]
    channel_join(token_2, channel_id)

    with pytest.raises(AccessError):
        channel_removeowner(token_2, channel_id, u_id_1)
