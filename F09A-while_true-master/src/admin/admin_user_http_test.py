"""
HTTP tests for the user_permission_change function.
Most tests have self-explanatory names.
"""

import pytest
from http_test import post
from error import InputError, AccessError

# pylint: disable=missing-docstring,redefined-outer-name,invalid-name

### setup ###

def http_user_permission_change(token, u_id, permission_id):
    return post("admin/userpermission/change", {"token": token, "u_id": u_id, \
                                                "permission_id": permission_id})

def http_auth_register(email, password, first, last):
    return post("auth/register", {"email": email, "password": password, \
                                  "name_first": first, "name_last": last})

def http_workspace_reset():
    post("workspace/reset")

@pytest.fixture(autouse=True)
def reset():
    http_workspace_reset()

NUM_USERS = 3
PERMISSION_OWNER = 1
PERMISSION_MEMBER = 2

@pytest.fixture
def users():
    users_list = []

    for i in range(0, NUM_USERS):
        users_list.append(http_auth_register("email" + str(i) + "@domain.com", \
                                             "a" * 8, "F" * 5, "L" * 5))

    return users_list

### test user_permission_change ###

def test_http_user_permission_change_missing_token(users):
    with pytest.raises(InputError):
        http_user_permission_change(None, users[1]["u_id"], PERMISSION_OWNER)

def test_http_user_permission_change_missing_u_id(users):
    with pytest.raises(InputError):
        http_user_permission_change(users[0]["token"], None, PERMISSION_OWNER)

def test_http_user_permission_change_missing_permission_id(users):
    with pytest.raises(InputError):
        http_user_permission_change(users[0]["token"], users[1]["u_id"], None)

def test_http_user_permission_change_invalid_token(users):
    with pytest.raises(AccessError):
        http_user_permission_change(users[0]["token"][:-1], users[1]["u_id"], PERMISSION_OWNER)

def test_http_user_permission_change_invalid_u_id(users):
    with pytest.raises(InputError):
        http_user_permission_change(users[0]["token"], 4, PERMISSION_OWNER)

def test_http_user_permission_change_invalid_permission_id(users):
    with pytest.raises(InputError):
        http_user_permission_change(users[0]["token"], users[1]["u_id"], 3)

def test_http_user_permission_change_not_owner(users):
    with pytest.raises(AccessError):
        http_user_permission_change(users[1]["token"], users[2]["u_id"], PERMISSION_OWNER)

def test_http_user_permission_change_promote_other(users):
    http_user_permission_change(users[0]["token"], users[1]["u_id"], PERMISSION_OWNER)
    # if user 0 successfully promoted user 1, user 1 should be able to promote user 2
    http_user_permission_change(users[1]["token"], users[2]["u_id"], PERMISSION_OWNER)

def test_http_user_permission_change_demote_self(users):
    http_user_permission_change(users[0]["token"], users[1]["u_id"], PERMISSION_OWNER)
    # if user 0 successfully promoted user 1, user 1 should be able to demote themself
    http_user_permission_change(users[1]["token"], users[1]["u_id"], PERMISSION_MEMBER)

def test_http_user_permission_change_demote_original(users):
    http_user_permission_change(users[0]["token"], users[1]["u_id"], PERMISSION_OWNER)
    # if user 0 successfully promoted user 1, user 1 should be able to demote the original user
    http_user_permission_change(users[1]["token"], users[0]["u_id"], PERMISSION_MEMBER)
