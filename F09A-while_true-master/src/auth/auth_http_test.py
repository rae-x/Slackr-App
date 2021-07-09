"""
HTTP tests for the auth functions.
Most tests have self-explanatory names.
"""

import pytest
from http_test import get, post
from error import InputError

# pylint: disable=missing-docstring,invalid-name

### setup ###

def http_auth_register(email, password, first, last):
    return post("auth/register", {"email": email, "password": password, \
                                  "name_first": first, "name_last": last})

def http_auth_login(email, password):
    return post("auth/login", {"email": email, "password": password})

def http_auth_logout(token):
    return post("auth/logout", {"token": token})

def http_user_profile(token, u_id):
    return get("user/profile", {"token": token, "u_id": u_id})

def http_workspace_reset():
    post("workspace/reset")

@pytest.fixture(autouse=True)
def reset():
    http_workspace_reset()

def is_valid(data):
    """
    Validates the output of auth_register and auth_login
    """
    return isinstance(data, dict) \
           and "u_id" in data \
           and "token" in data \
           and isinstance(data["u_id"], int) \
           and isinstance(data["token"], str) \

def user_handle(register_result):
    """
    Returns the handle of a user, with the data
    returned by auth_register (token, u_id)
    """
    return http_user_profile(register_result["token"], \
                             register_result["u_id"])["user"]["handle_str"]

EMAIL = "valid.email@domain.com"
PASSWORD = "a" * 8
FIRST = "F" * 5
LAST = "L" * 5

INVALID_EMAILS = ["domain.com", "@domain.com", ".@domain.com", \
"s p a c e s@domain.com", "email@domain", "<illegal.characters>@domain.com", "email"]

### test auth_register ###

# pass cases #

def test_http_auth_register_pass_normal():
    assert is_valid(http_auth_register(EMAIL, PASSWORD, FIRST, LAST))

def test_http_auth_register_pass_password_short():
    assert is_valid(http_auth_register(EMAIL, "a" * 6, FIRST, LAST))

def test_http_auth_register_pass_password_long():
    assert is_valid(http_auth_register(EMAIL, "a" * 64, FIRST, LAST))

def test_http_auth_register_pass_names_short():
    assert is_valid(http_auth_register(EMAIL, PASSWORD, "F", "L"))

def test_http_auth_register_pass_names_long():
    assert is_valid(http_auth_register(EMAIL, PASSWORD, "F" * 50, "L" * 50))

def test_http_auth_register_pass_double_same_password():
    assert is_valid(http_auth_register(EMAIL, PASSWORD, FIRST, LAST))
    assert is_valid(http_auth_register("second.email@domain.com", PASSWORD, "F2", "L2"))

def test_http_auth_register_pass_double_same_name():
    assert is_valid(http_auth_register(EMAIL, PASSWORD, FIRST, LAST))
    assert is_valid(http_auth_register("second.email@domain.com", PASSWORD, FIRST, LAST))

def test_http_auth_register_pass_handle_normal():
    result = http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert is_valid(result)
    assert user_handle(result) == (FIRST + LAST).lower()

def test_http_auth_register_pass_handle_case():
    result = http_auth_register(EMAIL, PASSWORD, "FfFf", "LlLl")
    assert is_valid(result)
    assert user_handle(result) == "ffffllll"

def test_http_auth_register_pass_handle_long():
    result = http_auth_register(EMAIL, PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result)
    assert user_handle(result) == "f" * 11 + "l" * 9

def test_http_auth_register_pass_handle_duplicate():
    result1 = http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert is_valid(result1)
    assert user_handle(result1) == (FIRST + LAST).lower()

    result2 = http_auth_register("second.email@domain.com", PASSWORD, FIRST, LAST)
    assert is_valid(result2)
    assert user_handle(result2) == (FIRST + LAST).lower() + "1"

def test_http_auth_register_pass_handle_duplicate_many():
    for i in range(101):
        result = http_auth_register(str(i) + "@domain.com", PASSWORD, FIRST, LAST)
        assert is_valid(result)

        expected_discriminator = ""
        if i > 0:
            expected_discriminator = str(i)

        assert user_handle(result) == (FIRST + LAST).lower() + expected_discriminator

def test_http_auth_register_pass_handle_long_duplicate():
    result1 = http_auth_register(EMAIL, PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result1)
    assert user_handle(result1) == "f" * 11 + "l" * 9

    result2 = http_auth_register("second.email@domain.com", PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result2)
    assert user_handle(result2) == "f" * 11 + "l" * 8 + "1"

def test_http_auth_register_pass_handle_long_many():
    result1 = http_auth_register(EMAIL, PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result1)
    assert user_handle(result1) == "f" * 11 + "l" * 9

    result2 = http_auth_register("second.email@domain.com", PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result2)
    assert user_handle(result2) == "f" * 11 + "l" * 8 + "1"

    for i in range(101):
        result = http_auth_register(str(i) + "@domain.com", PASSWORD, "F" * 11, "L" * 8 + "1")
        assert is_valid(result)
        expected_discriminator = str(i + 2)
        assert user_handle(result) == "f" * 11 + "l" * (9 - len(expected_discriminator)) \
                                                     + expected_discriminator

    for i in range(101):
        appended_discriminator = str(i + 2)
        result = http_auth_register(str(i + 101) + "@domain.com", PASSWORD, "F" * 11, \
                                    "L" * (9 - len(appended_discriminator)) \
                                        + appended_discriminator)
        assert is_valid(result)
        expected_discriminator = str(i + 101 + 2)
        assert user_handle(result) == "f" * 11 + "l" * (9 - len(expected_discriminator)) \
                                                     + expected_discriminator

# fail cases #

def test_http_auth_register_fail_missing_email():
    with pytest.raises(InputError):
        http_auth_register(None, PASSWORD, FIRST, LAST)

def test_http_auth_register_fail_missing_password():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, None, FIRST, LAST)

def test_http_auth_register_fail_missing_names():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, PASSWORD, None, None)

def test_http_auth_register_fail_wrong_type_email():
    with pytest.raises(InputError):
        http_auth_register(int("1" * 12), PASSWORD, FIRST, LAST)

def test_http_auth_register_fail_wrong_type_password():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, int("1" * 8), FIRST, LAST)

def test_http_auth_register_fail_wrong_type_names():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, PASSWORD, int("1" * 5), int("1" * 5))

def test_http_auth_register_fail_double_same_email():
    assert is_valid(http_auth_register(EMAIL, PASSWORD, FIRST, LAST))
    with pytest.raises(InputError):
        http_auth_register(EMAIL, PASSWORD, FIRST, LAST)

def test_http_auth_register_fail_email_invalid():
    for invalid_email in INVALID_EMAILS:
        with pytest.raises(InputError):
            http_auth_register(invalid_email, PASSWORD, FIRST, LAST)

def test_http_auth_register_fail_names_short():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, PASSWORD, "", "")

def test_http_auth_register_fail_names_long():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, PASSWORD, "F" * 51, "L" * 51)

def test_http_auth_register_fail_password_short():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, "a" * 5, FIRST, LAST)

def test_http_auth_register_fail_password_long():
    with pytest.raises(InputError):
        http_auth_register(EMAIL, "a" * 65, FIRST, LAST)

### test auth_login ###

# pass cases #

def test_http_auth_login_pass_normal():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert is_valid(http_auth_login(EMAIL, PASSWORD))

# fail cases #

def test_http_auth_login_fail_missing_email():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        http_auth_login(None, PASSWORD)

def test_http_auth_login_fail_missing_password():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        http_auth_login(EMAIL, None)

def test_http_auth_login_fail_wrong_type_email():
    http_auth_register(("1" * 12) + "@domain.com", PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        http_auth_login(int("1" * 12), PASSWORD)

def test_http_auth_login_fail_wrong_type_password():
    http_auth_register(EMAIL, "1" * 8, FIRST, LAST)
    with pytest.raises(InputError):
        http_auth_login(EMAIL, int("1" * 8))

def test_http_auth_login_fail_email_invalid():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    for invalid_email in INVALID_EMAILS:
        with pytest.raises(InputError):
            http_auth_login(invalid_email, PASSWORD)

def test_http_auth_login_fail_email_unknown():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        http_auth_login("second.email@domain.com", PASSWORD)

def test_http_auth_login_fail_password_incorrect():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        http_auth_login(EMAIL, "b" * 8)

### test auth_logout ###

# pass cases #

def test_http_auth_logout_normal():
    token = http_auth_register(EMAIL, PASSWORD, FIRST, LAST)["token"]
    assert http_auth_logout(token)["is_success"]

# fail cases #

def test_http_auth_logout_missing_token():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert not http_auth_logout(None)["is_success"]

def test_http_auth_logout_wrong_type_token():
    http_auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert not http_auth_logout(int("1" * 16))["is_success"]

def test_http_auth_logout_token_short():
    token = http_auth_register(EMAIL, PASSWORD, FIRST, LAST)["token"]
    assert not http_auth_logout(token[0:-1])["is_success"]

def test_http_auth_logout_double():
    token = http_auth_register(EMAIL, PASSWORD, FIRST, LAST)["token"]
    assert http_auth_logout(token)["is_success"]
    assert not http_auth_logout(token)["is_success"]
