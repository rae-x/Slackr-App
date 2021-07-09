'''
A file for the definitions of Message
'''
from data_store import database

# pylint: disable=missing-docstring, too-few-public-methods

class Message:
    """
    A message sent by a user on a channel
    """

    def __init__(self, user_id, channel_id, content, time_sent):
        self.message_id = database.generate_id("message")
        self.channel = channel_id
        self.sent_by = user_id
        self.content = content
        self.time_sent = time_sent
        self.reacts = {}
        self.pinned = False
