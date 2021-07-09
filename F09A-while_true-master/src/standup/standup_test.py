# pylint: disable=redefined-outer-name
'''
integration tests for standup
'''
from time import sleep
from datetime import datetime, timezone
import pytest
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create
from standup import standup_active, standup_send, standup_start
from workspace_reset import workspace_reset

@pytest.fixture(autouse=True)
def call_workspace_reset():
    '''
    auto reset between each function
    '''
    workspace_reset()

@pytest.fixture
def setup_user():
    '''
    setup an user using register
    '''
    data = auth_register("validemail@gmail.com", "123456", "John", "Citizen")
    return {"u_id":data["u_id"], "token":data["token"]}

@pytest.fixture
def setup_user2():
    '''
    setup an user using register
    '''
    data = auth_register("validemail1@gmail.com", "123456", "Hayden", "Smith")
    return {"u_id":data["u_id"], "token":data["token"]}

def test_standup_start_invalid_channelid(setup_user):
    '''
    test that standup raise input error for invalid channel id
    '''
    token = setup_user["token"]
    with pytest.raises(InputError):
        standup_start(token, "invalidchannelid", 1)
    sleep(2)

def test_standup_start_active(setup_user):
    '''
    test that standup raise input error for already active channel
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    standup_start(token, channel_id, 1)
    sleep(2)
    with pytest.raises(InputError):
        standup_start(token, channel_id, 1)

def test_standup_start_not_in_channel(setup_user, setup_user2):
    '''
    test that standup raise access error for user not in channel
    '''
    token1 = setup_user["token"]
    token2 = setup_user2["token"]
    channel_id = channels_create(token1, "Standup", True)["channel_id"]
    with pytest.raises(AccessError):
        standup_start(token2, channel_id, 1)
    sleep(2)

def test_standup_start_normal(setup_user):
    '''
    tests a normal case for standup start
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    time_finish = standup_start(token, channel_id, 1)
    time_start = datetime.utcnow()
    time_start = time_start.replace(tzinfo=timezone.utc).timestamp()
    assert time_start < time_finish["time_finish"] and \
        standup_active(token, channel_id)["is_active"] is True
    sleep(2)

def test_standup_active_invalid_channelid(setup_user):
    '''
    test for inputerror raised when channel id is invalid
    '''
    token = setup_user["token"]
    with pytest.raises(InputError):
        standup_active(token, "invalidchannelid")

def test_standup_active_false(setup_user):
    '''
    test for is_active == false when standup is not active
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    assert standup_active(token, channel_id)["is_active"] is False

def test_standup_active_true(setup_user):
    '''
    test for is_active == true when standup is active
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    standup_start(token, channel_id, 1)
    assert standup_active(token, channel_id)["is_active"] is True
    sleep(2)

def test_standup_active_wait(setup_user):
    '''
    test for standup active to be false after standup ended
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    standup_start(token, channel_id, 1)
    assert standup_active(token, channel_id)["is_active"] is True
    sleep(2)
    assert standup_active(token, channel_id)["is_active"] is False

def test_standup_active_not_in_channel(setup_user, setup_user2):
    '''
    test that standup raise access error for user not in channel
    '''
    token1 = setup_user["token"]
    token2 = setup_user2["token"]
    channel_id = channels_create(token1, "Standup", True)["channel_id"]
    with pytest.raises(AccessError):
        standup_active(token2, channel_id)

def test_standup_send_invalid_channelid(setup_user):
    '''
    test for inputerror raised for invalid channel id
    '''
    token = setup_user["token"]
    with pytest.raises(InputError):
        standup_send(token, "invalidchannelid", "message")

def test_standup_send_user_not_in_channel(setup_user, setup_user2):
    '''
    test for accesserror raised for user not in channel
    '''
    token = setup_user["token"]
    token2 = setup_user2["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    with pytest.raises(AccessError):
        standup_send(token2, channel_id, "message")

def test_standup_send_long_message(setup_user):
    '''
    test for inputerror raised for message > 1000 characters
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    standup_start(token, channel_id, 1)
    message = 'a' * 1001
    with pytest.raises(InputError):
        standup_send(token, channel_id, message)
    sleep(2)

def test_standup_send_not_active(setup_user):
    '''
    test for inputerror raised for channel not active
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    with pytest.raises(InputError):
        standup_send(token, channel_id, "message")

def test_standup_send_normal(setup_user):
    '''
    test for a normal case of standup_send
    '''
    token = setup_user["token"]
    channel_id = channels_create(token, "Standup", True)["channel_id"]
    standup_start(token, channel_id, 1)
    assert standup_send(token, channel_id, "message") == {}
    sleep(2)
