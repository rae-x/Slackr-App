"""
HTTP tests for the workspace_reset function.
Most tests have self-explanatory names.
"""

from http_test import get, post

# pylint: disable=missing-docstring

### setup ###

def http_workspace_reset():
    post("workspace/reset")

def http_auth_register(email, password, first, last):
    return post("auth/register", {"email": email, "password": password, \
                                  "name_first": first, "name_last": last})

def http_channels_create(token, name, is_public):
    return post("channels/create", {"token": token, "name": name, "is_public": is_public})

def http_channels_listall(token):
    return get("channels/listall", {"token": token})

def http_message_send(token, channel_id, message):
    return post("message/send", {"token": token, "channel_id": channel_id, "message": message})

def http_users_all(token):
    return get("users/all", {"token": token})

def http_user_profile(token, u_id):
    return get("user/profile", {"token": token, "u_id": u_id})

def http_search(token, query):
    return get("search", {"token": token, "query_str": query})

def make_user(index):
    """
    Creates a user (given an index to differentiate emails)
    """

    result = http_auth_register("email" + str(index) + "@domain.com", "a" * 8, "F" * 5, "L" * 5)

    return {"token": result["token"], "u_id": result["u_id"]}

### test workspace_reset ###

NUM = 10
def test_http_workspace_reset():
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
    http_workspace_reset()

    token = make_user(0)["token"]

    # range starts at 1 because
    # the first user is 0
    for i in range(1, NUM + 1):
        make_user(i)

    for i in range(NUM):
        http_channels_create(token, "channel" + str(i), True)

    channel_id = http_channels_listall(token)["channels"][0]["channel_id"]

    for i in range(NUM):
        http_message_send(token, channel_id, "message" + str(i))

    http_workspace_reset()

    # A user is required to check if everything is empty
    result = make_user(0)
    token = result["token"]
    u_id = result["u_id"]

    assert http_users_all(token)["users"] == [http_user_profile(token, u_id)["user"]]
    assert http_channels_listall(token)["channels"] == []
    assert http_search(token, "message")["messages"] == []
