"""
HTTP tests for the search function.
Most tests have self-explanatory names.
"""

import string
import pytest
from http_test import get, post

# pylint: disable=missing-docstring,line-too-long,redefined-outer-name,unused-variable,bad-continuation,invalid-name

### setup ###

NUM_USERS = 5
NUM_CHANNELS = 3
TRANSCRIPT = ["Now, fair Hippolyta, our nuptial hour", "Draws on apace; four happy days bring in", "Another moon: but, O, methinks, how slow", "This old moon wanes! she lingers my desires", "Like to a step-dame or a dowager", "Long withering out a young man revenue", "Four days will quickly steep themselves in night", "Four nights will quickly dream away the time", "And then the moon, like to a silver bow", "New-bent in heaven, shall behold the night", "Of our solemnities", "Go, Philostrate", "Stir up the Athenian youth to merriments", "Awake the pert and nimble spirit of mirth", "Turn melancholy forth to funerals", "The pale companion is not for our pomp", "Hippolyta, I woo'd thee with my sword", "And won thy love, doing thee injuries", "But I will wed thee in another key", "With pomp, with triumph and with revelling", "Happy be Theseus, our renowned duke!", "Thanks, good Egeus: what's the news with thee?"]

def http_search(token, query):
    return get("search", {"token": token, "query_str": query})["messages"]

def http_auth_register(email, password, first, last):
    return post("auth/register", {"email": email, "password": password, \
                                  "name_first": first, "name_last": last})

def http_auth_logout(token):
    return post("auth/logout", {"token": token})

def http_channels_create(token, name, is_public):
    return post("channels/create", {"token": token, "name": name, "is_public": is_public})

def http_channel_join(token, channel_id):
    return post("channel/join", {"token": token, "channel_id": channel_id})

def http_channel_messages(token, channel_id, start):
    return get("channel/messages", {"token": token, "channel_id": channel_id, "start": start})

def http_message_send(token, channel_id, message):
    return post("message/send", {"token": token, "channel_id": channel_id, "message": message})

def http_workspace_reset():
    post("workspace/reset")

@pytest.fixture(autouse=True)
def reset():
    http_workspace_reset()

@pytest.fixture
def setup_users():
    users = []

    for i in range(NUM_USERS):
        users.append(http_auth_register("email" + str(i) + "@domain.com", "a" * 8, "F" * 5, "L" * 5))

    return users[0]["token"], users

@pytest.fixture
def setup_channels(setup_users):
    token, users = setup_users

    channels = []
    for i in range(NUM_CHANNELS):
        channels.append(http_channels_create(token, "channel" + str(i), True))

        for user in users:
            if user["token"] != token:
                http_channel_join(user["token"], channels[-1]["channel_id"])

    return token, users, channels

@pytest.fixture
def setup(setup_channels):
    token, users, channels = setup_channels

    messages = {}
    current_user = 0
    current_channel = 0
    for message in TRANSCRIPT:
        http_message_send(users[current_user]["token"], channels[current_channel]["channel_id"], message)
        current_user += 1
        current_channel += 1
        if current_user >= len(users):
            current_user = 0
        if current_channel >= len(channels):
            current_channel = 0

    for channel in channels:
        messages_subset = http_channel_messages(token, channel["channel_id"], 0)["messages"]
        for message in messages_subset:
            messages[message["message"]] = message # create an entry in the messages dict
                                                   # with the key equal to the message
    return token, messages                         # content, and the value equal to the
                                                   # message dict

def result(messages, expected):
    """
    Generate a list of expected results for use in asserts
    """
    output = []
    for string in expected:
        if string in messages:
            output.append(messages[string])
    return output

def search_blank(token):
    """
    Helper function used for tests where no
    messages have been sent
    """
    assert http_search(token, "") == []
    assert http_search(token, "Hippolyta") == []

### test search ###

def test_http_search_missing_token(setup):
    token, messages = setup
    assert http_search(None, "methinks") == []

def test_http_search_missing_query(setup):
    token, messages = setup
    assert http_search(token, None) == []

def test_http_search_no_channels(setup_users):
    token, users = setup_users
    search_blank(token)

def test_http_search_no_messages(setup_channels):
    token, users, channels = setup_channels
    search_blank(token)

def test_http_search_empty_query(setup):
    token, messages = setup
    assert http_search(token, "") == []

def test_http_search_whitespace(setup):
    token, messages = setup
    assert http_search(token, " ") == []

def test_http_search_whitespace_repeated(setup):
    token, messages = setup
    assert http_search(token, " " * 8) == []

def test_http_search_whitespace_mixed(setup):
    token, messages = setup
    assert http_search(token, string.whitespace) == []

def test_http_search_word_single(setup):
    token, messages = setup
    assert http_search(token, "methinks") == result(messages, \
                                                   ["Another moon: but, O, methinks, how slow"])

def test_http_search_word_multiple(setup):
    token, messages = setup
    assert http_search(token, "Hippolyta") == result(messages,
                                                    ["Now, fair Hippolyta, our nuptial hour", \
                                                     "Hippolyta, I woo'd thee with my sword"])

def test_http_search_subword_single(setup):
    token, messages = setup
    assert http_search(token, "thenia") == result(messages, \
                                                 ["Stir up the Athenian youth to merriments"])

def test_http_search_subword_multiple(setup):
    token, messages = setup
    assert http_search(token, "nothe") == result(messages, \
                                                ["But I will wed thee in another key", \
                                                 "Another moon: but, O, methinks, how slow"])

def test_http_search_subword_whitespace(setup):
    token, messages = setup
    assert http_search(token, string.whitespace + "ompanio" + string.whitespace) == result(messages, \
                                                                                          ["The pale companion is not for our pomp"])

def test_http_search_multiple_words(setup):
    token, messages = setup
    assert http_search(token, "then the moon, like to a silver") == result(messages, \
                                                                          ["And then the moon, like to a silver bow"])

def test_http_search_different_case(setup):
    token, messages = setup
    assert http_search(token, "Egeus") \
        == http_search(token, "EGEUS") \
        == http_search(token, "egeus") \
        == http_search(token, "eGEUS") \
        == result(messages, \
                 ["Thanks, good Egeus: what's the news with thee?"])

# this must be the last test because
# the first user is logged out
def test_http_search_invalid_token(setup):
    token, messages = setup
    http_auth_logout(token)
    assert http_search(token, "Hippolyta") == []
# no more tests after this point;
# write tests above this function
