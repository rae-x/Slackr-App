"""
HTTP tests for the users_all function.
Most tests have self-explanatory names.
"""

import pytest
from http_test import get, post, put
from error import InputError

# pylint: disable=missing-docstring,redefined-outer-name,unused-variable,invalid-name


### setup ###

def http_users_all(token):
    """
    Convenience function to automatically extract
    the list of users from the returned dict
    """

    return get("users/all", {"token": token})["users"]

def http_user_profile(token, u_id):
    """
    Convenience function to automatically extract
    the user data from the returned dict
    """
    return get("user/profile", {"token": token, "u_id": u_id})["user"]

def http_auth_register(email, password, first, last):
    return post("auth/register", {"email": email, "password": password, \
                                  "name_first": first, "name_last": last})

def http_auth_logout(token):
    return post("auth/logout", {"token": token})

def http_user_profile_setname(token, first, last):
    return put("user/profile/setname", {"token": token, "name_first": first, "name_last": last})

def http_user_profile_setemail(token, email):
    return put("user/profile/setemail", {"token": token, "email": email})

def http_user_profile_sethandle(token, handle):
    return put("user/profile/sethandle", {"token": token, "handle": handle})

def http_workspace_reset():
    post("workspace/reset")

@pytest.fixture
def setup():
    http_workspace_reset()
    return make_user(0)

def make_user(index):
    """
    Creates a user (given an index to differentiate emails)
    """

    result = http_auth_register("email" + str(index) + "@domain.com", "a" * 8, "F" * 5, "L" * 5)
    token = result["token"]
    u_id = result["u_id"]

    return token, http_user_profile(token, u_id)

### test users_all ###

def test_http_users_all_missing_token(setup):
    token, user = setup
    with pytest.raises(InputError):
        http_users_all(None)

def test_http_users_all_one(setup):
    token, user = setup
    assert http_users_all(token) == [user]

NUM_USERS = 10
def test_http_users_all_many(setup):
    token, user = setup

    tokens = [token]
    users = [user]
    for i in range(1, NUM_USERS + 1):
        token, user = make_user(i)
        tokens.append(token)
        users.append(user)

    assert http_users_all(token) == users

    for this_token in tokens:
        assert http_users_all(this_token) == users

def test_http_users_all_change_name(setup):
    token, user = setup
    http_user_profile_setname(token, "G" * 5, "M" * 5)
    user = http_user_profile(token, user["u_id"])
    assert http_users_all(token) == [user]

def test_http_users_all_change_email(setup):
    token, user = setup
    http_user_profile_setemail(token, "second.email@domain.com")
    user = http_user_profile(token, user["u_id"])
    assert http_users_all(token) == [user]

def test_http_users_all_change_handle(setup):
    token, user = setup
    http_user_profile_sethandle(token, "H" * 8)
    user = http_user_profile(token, user["u_id"])
    assert http_users_all(token) == [user]

# this must be the last test because
# the first user is logged out
def test_http_users_all_invalid_token(setup):
    token, user = setup
    http_auth_logout(token)
    assert http_users_all(token) == []
# no more tests after this point;
# write tests above this function
