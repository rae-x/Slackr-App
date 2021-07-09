"""
Tests for the workspace_reset function.
Most tests have self-explanatory names.
"""

from workspace_reset import workspace_reset
from auth import auth_register
from channels import channels_create, channels_listall
from message import message_send
from users_all import users_all
from user_profile import user_profile
from search import search

### setup ###

def make_user(index):
    """
    Creates a user (given an index to differentiate emails)
    """

    result = auth_register("email" + str(index) + "@domain.com", "a" * 8, "F" * 5, "L" * 5)

    return {"token": result["token"], "u_id": result["u_id"]}

### test workspace_reset ###

NUM = 10
def test_workspace_reset():
    """
    Tests workspace_reset by first clearing
    the database, then loading it data and
    clearing it again. At this point, it is
    asserted that users_all, channels_listall
    and search return empty results.
    """

    # Init the database and clear its data.
    # While it may seem like we are relying
    # on the very function we are testing
    # to make the tests work, calling this
    # at the start is in fact required to
    # make it work, and if there is a
    # problem, this will be picked up
    # while running the test.
    workspace_reset()

    token = make_user(0)["token"]

    # range starts at 1 because
    # the first user is 0
    for i in range(1, NUM + 1):
        make_user(i)

    for i in range(NUM):
        channels_create(token, "channel" + str(i), True)

    channel_id = channels_listall(token)["channels"][0]["channel_id"]

    for i in range(NUM):
        message_send(token, channel_id, "message" + str(i))

    workspace_reset()

    # A user is required to check if everything is empty
    result = make_user(0)
    token = result["token"]
    u_id = result["u_id"]

    assert users_all(token)["users"] == [user_profile(token, u_id)["user"]]
    assert channels_listall(token)["channels"] == []
    assert search(token, "message")["messages"] == []
