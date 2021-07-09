"""
Tests for the users_all function.
Most tests have self-explanatory names.
"""

import pytest
import users_all as _users_all # named like this to avoid a namespace
                               # conflict with the users_all wrapper
                               # function in this file
from auth import auth_register, auth_logout
import user_profile as _user_profile # named like this to avoid a namespace
                                     # conflict with the user_profile wrapper
                                     # function in this file
from user_profile import user_profile_setname, user_profile_setemail, user_profile_sethandle
from workspace_reset import workspace_reset

# pylint: disable=missing-docstring,redefined-outer-name,unused-variable

### setup ###

def users_all(token):
    """
    Convenience function to automatically extract
    the list of users from the returned dict
    """
    return _users_all.users_all(token)["users"]

def user_profile(token, u_id):
    """
    Convenience function to automatically extract
    the user data from the returned dict
    """
    return _user_profile.user_profile(token, u_id)["user"]

def make_user(index):
    """
    Creates a user (given an index to differentiate emails)
    """

    result = auth_register("email" + str(index) + "@domain.com", "a" * 8, "F" * 5, "L" * 5)
    token = result["token"]
    u_id = result["u_id"]

    return token, user_profile(token, u_id)

@pytest.fixture
def setup():
    workspace_reset()
    return make_user(0)

### test users_all ###

def test_users_all_one(setup):
    token, user = setup
    assert users_all(token) == [user]

NUM_USERS = 10
def test_users_all_many(setup):
    token, user = setup

    tokens = [token]
    users = [user]
    for i in range(1, NUM_USERS + 1):
        token, user = make_user(i)
        tokens.append(token)
        users.append(user)

    assert users_all(token) == users

    for this_token in tokens:
        assert users_all(this_token) == users

def test_users_all_change_name(setup):
    token, user = setup
    user_profile_setname(token, "G" * 5, "M" * 5)
    user = user_profile(token, user["u_id"])
    assert users_all(token) == [user]

def test_users_all_change_email(setup):
    token, user = setup
    user_profile_setemail(token, "second.email@domain.com")
    user = user_profile(token, user["u_id"])
    assert users_all(token) == [user]

def test_users_all_change_handle(setup):
    token, user = setup
    user_profile_sethandle(token, "H" * 8)
    user = user_profile(token, user["u_id"])
    assert users_all(token) == [user]

# this must be the last test because
# the first user is logged out
def test_users_all_invalid_token(setup):
    token, user = setup
    auth_logout(token)
    assert users_all(token) == []
# no more tests after this point;
# write tests above this function
