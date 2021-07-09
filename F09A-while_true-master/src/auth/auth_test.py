"""
Tests for the auth functions.
Most tests have self-explanatory names.
"""

import pytest
from auth import auth_register, auth_login, auth_logout
from user_profile import user_profile
from error import InputError
from workspace_reset import workspace_reset

# pylint: disable=missing-docstring,invalid-name

### setup ###

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
    return user_profile(register_result["token"], register_result["u_id"])["user"]["handle_str"]

EMAIL = "valid.email@domain.com"
PASSWORD = "a" * 8
FIRST = "F" * 5
LAST = "L" * 5

INVALID_EMAILS = ["domain.com", "@domain.com", ".@domain.com", \
"s p a c e s@domain.com", "email@domain", "<illegal.characters>@domain.com", "email"]

@pytest.fixture(autouse=True)
def reset():
    workspace_reset()

### test auth_register ###

# pass cases #

def test_auth_register_pass_normal():
    assert is_valid(auth_register(EMAIL, PASSWORD, FIRST, LAST))

def test_auth_register_pass_password_short():
    assert is_valid(auth_register(EMAIL, "a" * 6, FIRST, LAST))

def test_auth_register_pass_password_long():
    assert is_valid(auth_register(EMAIL, "a" * 64, FIRST, LAST))

def test_auth_register_pass_names_short():
    assert is_valid(auth_register(EMAIL, PASSWORD, "F", "L"))

def test_auth_register_pass_names_long():
    assert is_valid(auth_register(EMAIL, PASSWORD, "F" * 50, "L" * 50))

def test_auth_register_pass_double_same_password():
    assert is_valid(auth_register(EMAIL, PASSWORD, FIRST, LAST))
    assert is_valid(auth_register("second.email@domain.com", PASSWORD, "F2", "L2"))

def test_auth_register_pass_double_same_name():
    assert is_valid(auth_register(EMAIL, PASSWORD, FIRST, LAST))
    assert is_valid(auth_register("second.email@domain.com", PASSWORD, FIRST, LAST))

def test_auth_register_pass_handle_normal():
    result = auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert is_valid(result)
    assert user_handle(result) == (FIRST + LAST).lower()

def test_auth_register_pass_handle_case():
    result = auth_register(EMAIL, PASSWORD, "FfFf", "LlLl")
    assert is_valid(result)
    assert user_handle(result) == "ffffllll"

def test_auth_register_pass_handle_long():
    result = auth_register(EMAIL, PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result)
    assert user_handle(result) == "f" * 11 + "l" * 9

def test_auth_register_pass_handle_duplicate():
    result1 = auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert is_valid(result1)
    assert user_handle(result1) == (FIRST + LAST).lower()

    result2 = auth_register("second.email@domain.com", PASSWORD, FIRST, LAST)
    assert is_valid(result2)
    assert user_handle(result2) == (FIRST + LAST).lower() + "1"

def test_auth_register_pass_handle_duplicate_many():
    for i in range(101):
        result = auth_register(str(i) + "@domain.com", PASSWORD, FIRST, LAST)
        assert is_valid(result)

        expected_discriminator = ""
        if i > 0:
            expected_discriminator = str(i)

        assert user_handle(result) == (FIRST + LAST).lower() + expected_discriminator

def test_auth_register_pass_handle_long_duplicate():
    result1 = auth_register(EMAIL, PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result1)
    assert user_handle(result1) == "f" * 11 + "l" * 9

    result2 = auth_register("second.email@domain.com", PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result2)
    assert user_handle(result2) == "f" * 11 + "l" * 8 + "1"

def test_auth_register_pass_handle_long_quadruplicate():
    result1 = auth_register(EMAIL, PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result1)
    assert user_handle(result1) == "f" * 11 + "l" * 9

    result2 = auth_register("second.email@domain.com", PASSWORD, "F" * 11, "L" * 11)
    assert is_valid(result2)
    assert user_handle(result2) == "f" * 11 + "l" * 8 + "1"

    for i in range(101):
        result = auth_register(str(i) + "@domain.com", PASSWORD, "F" * 11, "L" * 8 + "1")
        assert is_valid(result)
        expected_discriminator = str(i + 2)
        assert user_handle(result) == "f" * 11 + "l" * (9 - len(expected_discriminator)) \
                                                     + expected_discriminator

    for i in range(101):
        appended_discriminator = str(i + 2)
        result = auth_register(str(i + 101) + "@domain.com", PASSWORD, "F" * 11, \
                               "L" * (9 - len(appended_discriminator)) + appended_discriminator)
        assert is_valid(result)
        expected_discriminator = str(i + 101 + 2)
        assert user_handle(result) == "f" * 11 + "l" * (9 - len(expected_discriminator)) \
                                                     + expected_discriminator

# fail cases #

def test_auth_register_fail_wrong_type_email():
    with pytest.raises(InputError):
        auth_register(int("1" * 12), PASSWORD, FIRST, LAST)

def test_auth_register_fail_wrong_type_password():
    with pytest.raises(InputError):
        auth_register(EMAIL, int("1" * 8), FIRST, LAST)

def test_auth_register_fail_wrong_type_names():
    with pytest.raises(InputError):
        auth_register(EMAIL, PASSWORD, int("1" * 5), int("1" * 5))

def test_auth_register_fail_double_same_email():
    assert is_valid(auth_register(EMAIL, PASSWORD, FIRST, LAST))
    with pytest.raises(InputError):
        auth_register(EMAIL, PASSWORD, FIRST, LAST)

def test_auth_register_fail_email_invalid():
    for invalid_email in INVALID_EMAILS:
        with pytest.raises(InputError):
            auth_register(invalid_email, PASSWORD, FIRST, LAST)

def test_auth_register_fail_names_short():
    with pytest.raises(InputError):
        auth_register(EMAIL, PASSWORD, "", "")

def test_auth_register_fail_names_long():
    with pytest.raises(InputError):
        auth_register(EMAIL, PASSWORD, "F" * 51, "L" * 51)

def test_auth_register_fail_password_short():
    with pytest.raises(InputError):
        auth_register(EMAIL, "a" * 5, FIRST, LAST)

def test_auth_register_fail_password_long():
    with pytest.raises(InputError):
        auth_register(EMAIL, "a" * 65, FIRST, LAST)

### test auth_login ###

# pass cases #

def test_auth_login_pass_normal():
    auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert is_valid(auth_login(EMAIL, PASSWORD))

# fail cases #

def test_auth_login_fail_wrong_type_email():
    auth_register(("1" * 12) + "@domain.com", PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        auth_login(int("1" * 12), PASSWORD)

def test_auth_login_fail_wrong_type_password():
    auth_register(EMAIL, "1" * 8, FIRST, LAST)
    with pytest.raises(InputError):
        auth_login(EMAIL, int("1" * 8))

def test_auth_login_fail_email_invalid():
    auth_register(EMAIL, PASSWORD, FIRST, LAST)
    for invalid_email in INVALID_EMAILS:
        with pytest.raises(InputError):
            auth_login(invalid_email, PASSWORD)

def test_auth_login_fail_email_unknown():
    auth_register(EMAIL, PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        auth_login("second.email@domain.com", PASSWORD)

def test_auth_login_fail_password_incorrect():
    auth_register(EMAIL, PASSWORD, FIRST, LAST)
    with pytest.raises(InputError):
        auth_login(EMAIL, "b" * 8)

### test auth_logout ###

# pass cases #

def test_auth_logout_normal():
    token = auth_register(EMAIL, PASSWORD, FIRST, LAST)["token"]
    assert auth_logout(token)["is_success"]

# fail cases #

def test_auth_logout_token_wrong_type():
    auth_register(EMAIL, PASSWORD, FIRST, LAST)
    assert not auth_logout(int("1" * 16))["is_success"]

def test_auth_logout_token_short():
    token = auth_register(EMAIL, PASSWORD, FIRST, LAST)["token"]
    assert not auth_logout(token[0:-1])["is_success"]

def test_auth_logout_double():
    token = auth_register(EMAIL, PASSWORD, FIRST, LAST)["token"]
    assert auth_logout(token)["is_success"]
    assert not auth_logout(token)["is_success"]
