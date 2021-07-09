import pytest
from auth import auth_register, auth_login, auth_logout
from error import InputError
import data_store

@pytest.fixture
def reset():
    data_store.setup_data_store()

### setup ###

#expected_id = 0
def is_valid(data):
    #global expected_id
    #expected_id += 1
    return type(data) is dict \
           and "u_id" in data \
           and "token" in data \
           and type(data["u_id"]) is int \
           and type(data["token"]) is str \
           # and data["u_id"] == expected_id \
           # and len(data["token"]) == 16 \

email = "valid.email@domain.com"
password = "a" * 8
first = "F" * 5
last = "L" * 5

invalid_emails = ["domain.com", "@domain.com", ".@domain.com", "s p a c e s@domain.com", "email@domain", "<illegal.characters>@domain.com", "email"]

### test auth_register ###

# pass cases #

def test_auth_register_pass_normal(reset):
    assert is_valid(auth_register(email, password, first, last))

def test_auth_register_pass_password_short(reset):
    assert is_valid(auth_register(email, "a" * 6, first, last))

def test_auth_register_pass_password_long(reset):
    assert is_valid(auth_register(email, "a" * 64, first, last))

def test_auth_register_pass_names_short(reset):
    assert is_valid(auth_register(email, password, "F", "L"))

def test_auth_register_pass_names_long(reset):
    assert is_valid(auth_register(email, password, "F" * 50, "L" * 50))

def test_auth_register_pass_double_same_password(reset):
    assert is_valid(auth_register(email, password, first, last))
    assert is_valid(auth_register("second.email@domain.com", password, "F2", "L2"))

def test_auth_register_pass_double_same_name(reset):
    assert is_valid(auth_register(email, password, first, last))
    assert is_valid(auth_register("second.email@domain.com", password, first, last))

# fail cases #

def test_auth_register_fail_wrong_type_email(reset):
    with pytest.raises(InputError):
        auth_register(int("1" * 12), password, first, last)

def test_auth_register_fail_wrong_type_password(reset):
    with pytest.raises(InputError):
        auth_register(email, int("1" * 8), first, last)

def test_auth_register_fail_wrong_type_names(reset):
    with pytest.raises(InputError):
        auth_register(email, password, int("1" * 5), int("1" * 5))

def test_auth_register_fail_double_same_email(reset):
    assert is_valid(auth_register(email, password, first, last))
    with pytest.raises(InputError):
        auth_register(email, password, first, last)

def test_auth_register_fail_email_invalid(reset):
    for invalid_email in invalid_emails:
        with pytest.raises(InputError):
            auth_register(invalid_email, password, first, last)

def test_auth_register_fail_names_short(reset):
    with pytest.raises(InputError):
        auth_register(email, password, "", "")

def test_auth_register_fail_names_long(reset):
    with pytest.raises(InputError):
        auth_register(email, password, "F" * 51, "L" * 51)

def test_auth_register_fail_password_short(reset):
    with pytest.raises(InputError):
        auth_register(email, "a" * 5, first, last)

def test_auth_register_fail_password_long(reset):
    with pytest.raises(InputError):
        auth_register(email, "a" * 65, first, last)

### test auth_login ###

# pass cases #

def test_auth_login_pass_normal(reset):
    auth_register(email, password, first, last)
    assert is_valid(auth_login(email, password))

# fail cases #

def test_auth_login_fail_wrong_type_email(reset):
    auth_register(("1" * 12) + "@domain.com", password, first, last)
    with pytest.raises(InputError):
        auth_login(int("1" * 12), password)

def test_auth_login_fail_wrong_type_password(reset):
    auth_register(email, "1" * 8, first, last)
    with pytest.raises(InputError):
        auth_login(email, int("1" * 8))

def test_auth_login_fail_email_invalid(reset):
    auth_register(email, password, first, last)
    for invalid_email in invalid_emails:
        with pytest.raises(InputError):
            auth_login(invalid_email, password)

def test_auth_login_fail_email_unknown(reset):
    auth_register(email, password, first, last)
    with pytest.raises(InputError):
        auth_login("second.email@domain.com", password)

def test_auth_login_fail_password_incorrect(reset):
    auth_register(email, password, first, last)
    with pytest.raises(InputError):
        auth_login(email, "b" * 8)

### test auth_logout ###

# pass cases #

def test_auth_logout_normal(reset):
    token = auth_register(email, password, first, last)["token"]
    assert auth_logout(token)["is_success"] == True

# fail cases #

def test_auth_logout_token_wrong_type(reset):
    auth_register(email, password, first, last)
    assert auth_logout(int("1" * 16))["is_success"] == False

def test_auth_logout_token_short(reset):
    token = auth_register(email, password, first, last)["token"]
    assert auth_logout(token[0:-1])["is_success"] == False

def test_auth_logout_double(reset):
    token = auth_register(email, password, first, last)["token"]
    assert auth_logout(token)["is_success"] == True
    assert auth_logout(token)["is_success"] == False
