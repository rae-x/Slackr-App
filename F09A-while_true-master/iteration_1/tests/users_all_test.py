import pytest
import other
from auth import auth_register, auth_logout
import user
from user import user_profile_setname, user_profile_setemail, user_profile_sethandle
from error import AccessError

### setup ###

# convenience function to automatically extract
# the list of users from the returned dict
def users_all(token):
    return other.users_all(token)["users"]

# convenience function to automatically extract
# the list of users from the returned dict
def user_profile(token, u_id):
    return user.user_profile(token, u_id)["user"]

def make_user(i):
    result = auth_register("email" + str(i) + "@domain.com", "a" * 8, "F" * 5, "L" * 5)
    token = result["token"]
    u_id = result["u_id"]

    return token, user_profile(token, u_id)

@pytest.fixture
def setup():
    return make_user(0)

### test users_all ###

def test_users_all_one(setup):
    token, user = setup
    assert(users_all(token) == [user])

num_users = 10
def test_users_all_many(setup):
    token, user = setup

    tokens = []
    users = []
    for i in range(1, num_users + 1):
        token, user = make_user(i)
        tokens.append(token)
        users.append(users)

    assert(users_all(token) == users)

    for this_token in tokens:
        assert(users_all(this_token) == users)

def test_users_all_change_name(setup):
    token, user = setup
    user_profile_setname(token, "G" * 5, "M" * 5)
    user = user_profile(token, user["u_id"])
    assert(users_all(token) == [user])

def test_users_all_change_email(setup):
    token, user = setup
    user_profile_setemail(token, "second.email@domain.com")
    user = user_profile(token, user["u_id"])
    assert(users_all(token) == [user])

def test_users_all_change_handle(setup):
    token, user = setup
    user_profile_sethandle(token, "H" * 8)
    user = user_profile(token, user["u_id"])
    assert(users_all(token) == [user])

# this must be the last test because
# the first user is logged out
def test_users_all_invalid_token(setup):
    token, user = setup
    auth_logout(token)
    with pytest.raises(AccessError):
        users_all(token)
# no more tests after this point;
# write tests above this function
