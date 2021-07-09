"""
Tests for the admin_user_permission_change function.
Most tests have self-explanatory names.
"""

import pytest
from admin_user import admin_user_permission_change, admin_user_remove
from auth import auth_register
from error import InputError, AccessError
from workspace_reset import workspace_reset

# pylint: disable=missing-docstring,redefined-outer-name,invalid-name, expression-not-assigned, unused-variable

### setup ###

@pytest.fixture(autouse=True)
def reset():
    workspace_reset()

NUM_USERS = 3
PERMISSION_OWNER = 1
PERMISSION_MEMBER = 2

@pytest.fixture
def users():
    users_list = []

    for i in range(0, NUM_USERS):
        users_list.append(auth_register("email" + str(i) + "@domain.com", \
                                        "a" * 8, "F" * 5, "L" * 5))

    return users_list

### test admin_user_permission_change ###

def test_admin_user_permission_change_invalid_token(users):
    with pytest.raises(AccessError):
        admin_user_permission_change(users[0]["token"][:-1], users[1]["u_id"], PERMISSION_OWNER)

def test_admin_user_permission_change_invalid_u_id(users):
    with pytest.raises(InputError):
        admin_user_permission_change(users[0]["token"], 4, PERMISSION_OWNER)

def test_admin_user_permission_change_invalid_permission_id(users):
    with pytest.raises(InputError):
        admin_user_permission_change(users[0]["token"], users[1]["u_id"], 3)

def test_admin_user_permission_change_not_owner(users):
    with pytest.raises(AccessError):
        admin_user_permission_change(users[1]["token"], users[2]["u_id"], PERMISSION_OWNER)

def test_admin_user_permission_change_promote_other(users):
    admin_user_permission_change(users[0]["token"], users[1]["u_id"], PERMISSION_OWNER)
    # if user 0 successfully promoted user 1, user 1 should be able to promote user 2
    admin_user_permission_change(users[1]["token"], users[2]["u_id"], PERMISSION_OWNER)

def test_admin_user_permission_change_demote_self(users):
    admin_user_permission_change(users[0]["token"], users[1]["u_id"], PERMISSION_OWNER)
    # if user 0 successfully promoted user 1, user 1 should be able to demote themself
    admin_user_permission_change(users[1]["token"], users[1]["u_id"], PERMISSION_MEMBER)

def test_admin_user_permission_change_demote_original(users):
    admin_user_permission_change(users[0]["token"], users[1]["u_id"], PERMISSION_OWNER)
    # if user 0 successfully promoted user 1, user 1 should be able to demote the original user
    admin_user_permission_change(users[1]["token"], users[0]["u_id"], PERMISSION_MEMBER)


# test admin_user_remove

def test_admin_useremove_valid(users):
    '''
    Testing a successful user removal
    '''
    user_first, user_second = users[0], users[1]
    token = user_first['token']

    assert admin_user_remove(token, user_second['u_id']) == {}

def test_admin_userremove_invalidtoken(users):
    '''
    Testing removing a user with an invalid token
    '''
    user_first, user_second = users[0], users[1]
    fake_token = 'fake'

    with pytest.raises(AccessError) as _:
        admin_user_remove(fake_token, user_second['u_id']) == {}

def test_admin_userremove_invalid_uid(users):
    '''
    Testing removing a user that does not exist
    '''
    user_first, user_second = users[0], users[1]
    token = user_first['token']
    fake_id = -1

    with pytest.raises(InputError) as _:
        admin_user_remove(token, fake_id)

def test_admin_userremove_unauthorised(users):
    '''
    Testing having a non-admin attempt to remove a user
    '''
    user_first, user_second = users[0], users[1]
    token = user_first['token']
    admin_user_permission_change(token, user_first['u_id'], PERMISSION_MEMBER)

    with pytest.raises(AccessError) as _:
        admin_user_remove(token, user_second['u_id'])
