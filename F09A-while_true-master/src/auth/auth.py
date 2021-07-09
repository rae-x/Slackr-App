"""
Contains auth functions and their HTTP routes
"""

### Builtin/pip Modules ###
import re
import random
import string
from uuid import uuid4
from json import dumps
from flask import request, Blueprint
import smtplib
import ssl

### Package Modules ###
from error import InputError
from data_store import database
from user_definition import User

### Page Blueprint ###
AUTH_PAGE = Blueprint("auth_page", __name__)

### Host Credentials for sending password resets ###
# In practice, never, ever put credentials in code
HOST_EMAIL = "f09whiletrue@gmail.com"
HOST_PASSWORD = "whiletrue@F09"

### Reset Code Length ###
RESET_CODE_LEN = 6

### Routes ###

@AUTH_PAGE.route("/auth/register", methods=["POST"])
def route_auth_register():
    """
    HTTP route for auth_register
    """

    payload = request.get_json()

    email = payload.get("email")
    password = payload.get("password")
    first = payload.get("name_first")
    last = payload.get("name_last")

    return dumps(auth_register(email, password, first, last))

@AUTH_PAGE.route("/auth/login", methods=["POST"])
def route_auth_login():
    """
    HTTP route for auth_login
    """

    payload = request.get_json()

    email = payload.get("email")
    password = payload.get("password")

    return dumps(auth_login(email, password))

@AUTH_PAGE.route("/auth/logout", methods=["POST"])
def route_auth_logout():
    """
    HTTP route for auth_logout
    """

    payload = request.get_json()

    token = payload.get("token")

    return dumps(auth_logout(token))

@AUTH_PAGE.route("/auth/passwordreset/request", methods=["POST"])
def route_auth_passwordreset_request():
    """
    HTTP route for auth_passwordreset_request
    """

    payload = request.get_json()

    email = payload.get("email")

    return dumps(auth_passwordreset_request(email))

@AUTH_PAGE.route("/auth/passwordreset/reset", methods=["POST"])
def route_auth_passwordreset_reset():
    """
    HTTP route for auth_passwordreset_reset
    """

    payload = request.get_json()

    reset_code = payload.get("reset_code")
    new_password = payload.get("new_password")

    return dumps(auth_passwordreset_reset(reset_code, new_password))

### Functions ###

def auth_register(email, password, first, last):
    """
    Registers a new user. Returns their id and token.
    """

    if not isinstance(email, str) or not isinstance(password, str) \
    or not isinstance(first, str) or not isinstance(last, str):
        raise InputError(description="Input error: invalid arguments")

    if not email_valid(email):
        raise InputError(description="Input error: email is not valid")

    check_length(password, "password", 6, 64)
    check_length(first, "first name", 1, 50)
    check_length(last, "last name", 1, 50)

    if database.email_in_use(email):
        raise InputError(description="Input error: email is already in use")

    handle, original_handle = generate_handle(first, last)

    new_user = User(email, password, first, last, handle, original_handle)
    database.users.append(new_user)
    if len(database.slackr_owner_ids) == 0:
        database.add_owner(new_user)

    token = generate_token(new_user.user_id)

    database.update()

    return {"u_id": new_user.user_id, "token": token}

def auth_login(email, password):
    """
    Logs an existing user in. Returns their id and token.
    """

    if not isinstance(email, str) or not isinstance(password, str):
        raise InputError(description="Input error: invalid arguments")

    if not email_valid(email):
        raise InputError(description="Input error: email is not valid")

    for user in database.users:
        if user.email == email:
            if user.password != password:
                raise InputError(description="Input error: password is not correct")

            token = generate_token(user.user_id)
            database.update()

            return {"u_id": user.user_id, "token": token}

    raise InputError(description="Input error: email does not belong to a user")

def auth_logout(token):
    """
    Logs an existing user out. Returns an indication of success.
    """

    if not isinstance(token, str):
        return {"is_success": False}

    if database.get_authed_user(token, error=False):
        del database.active_tokens[token]
        database.update()

        return {"is_success": True}

    return {"is_success": False}

def auth_passwordreset_request(email):
    """
    Sends the email address an email containing a secret code to which
    can be used to reset their password through /auth/passwordreset/reset
    """
    u_id = database.get_user_by_email(email).user_id
    if (u_id == None):
        # Early return. This function should not raise any errors
        return {}

    reset_code = generate_reset_code(u_id)
    message = "Reset Code is " + reset_code

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", context=context) as email_server:
        email_server.login(HOST_EMAIL, HOST_PASSWORD)
        email_server.sendmail(HOST_EMAIL, email, message)

    return {}

def auth_passwordreset_reset(reset_code, new_password):
    """
    Given the reset code, the user's password is reset and changed to the
    new password inputted
    """
    if reset_code not in database.password_reset_codes:
        raise InputError(description="Input error: reset code is not valid")

    check_length(new_password, "password", 6, 64)

    user = database.get_user(database.password_reset_codes[reset_code])
    user.password = new_password
    del database.password_reset_codes[reset_code]

    return {}

### Helper Functions ###

def email_valid(email):
    """
    Validates an email address
    """
    return re.match(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", email) is not None

def check_length(string, name, min_len, max_len):
    """
    Checks that the length of a string is between `min` and `max`.
    The argument `name` is used in the human-readable InputError
    message which is thrown if the check is failed.
    """

    if len(string) < min_len:
        raise InputError(description="Input error: " + name + " must contain " \
                                                     + str(min_len) + " or more characters")

    if len(string) > max_len:
        raise InputError(description="Input error: " + name + " must contain " \
                                                     + str(max_len) + " or less characters")

def generate_token(user_id):
    """
    Generates an auth token
    """
    token = str(uuid4())
    database.active_tokens[token] = user_id
    return token

def generate_reset_code(user_id):
    """
    Generates a reset code
    """
    reset_code = "".join(random.choices(string.ascii_uppercase + \
            string.ascii_lowercase + string.digits, k=RESET_CODE_LEN))
    database.password_reset_codes[reset_code] = user_id
    return reset_code

def count_duplicates(handle):
    """
    Counts the number of users with the given handle
    """

    count = 0
    if handle == "hangman": count = 1

    for user in database.users:
        if handle in (user.handle, user.original_handle):
            count += 1

    return count

def generate_handle(first, last=None, count=0):
    """
    Generates a unqie user handle based on the concatenation
    of their first and last names. Changes are made to ensure
    uniqueness and that it complies with the size limit.
    """

    if last is None:
        handle = first
    else:
        handle = first.lower() + last.lower()

    if len(handle) > User.HANDLE_MAX_LENGTH:
        handle = handle[0:User.HANDLE_MAX_LENGTH]

    original_handle = handle

    duplicate_count = count_duplicates(handle)

    if duplicate_count > 0:
        if count == 0:
            discriminator = str(duplicate_count)
        else:
            discriminator = str(count)

        possible_change = handle[0:User.HANDLE_MAX_LENGTH - len(discriminator)] + discriminator

        if count_duplicates(possible_change) > 0:
            handle, original_handle = generate_handle(possible_change, count=count + 1)
        else:
            handle = possible_change

    return (handle, original_handle)
