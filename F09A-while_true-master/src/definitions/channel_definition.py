'''
A file for the definitions of Channel
'''
from time import time
from data_store import database

# pylint: disable=missing-docstring, too-many-instance-attributes

class Channel:
    """
    A channel on which messages can be sent within the app
    """

    def __init__(self, name, is_public):
        self.channel_id = database.generate_id("channel")
        self.name = name
        self.is_public = is_public
        self.owners = []
        self.members = []

        # The following fields are for standups
        self.is_active = False
        self.time_finish = None
        self.buffer = []

        self.hangman_active = False

    def add_member(self, user):
        if user and user not in self.members:
            self.members.append(user)

    def remove_member(self, user):
        self.remove_owner(user)
        if user and user in self.members:
            self.members.remove(user)

    def add_owner(self, user):
        if user and user not in self.owners:
            self.owners.append(user)

    def remove_owner(self, user):
        if user and user in self.owners:
            self.owners.remove(user)

    def has_member(self, user):
        return user in self.members

    def has_owner(self, user):
        return user in self.owners

    def json(self):
        return {
            "name": self.name,
            "owner_members": self.json_members(self.owners),
            "all_members": self.json_members(self.members)
        }

    @classmethod
    def json_members(cls, member_list):
        return [user.json_member() for user in member_list]

    def json_messages(self, user):
        """
        Returns all of the channel's messages that were sent at the current
        time or in the past, in json format
        """
        messages = []

        for message in database.messages:
            now = int(time())
            if message.channel == self.channel_id and message.time_sent <= now + 2:
                reacts = []

                for key in message.reacts:
                    user_reacted = user.user_id in message.reacts[key]
                    reacts.append({"react_id": key,
                                   "u_ids": message.reacts[key],
                                   "is_this_user_reacted": user_reacted})

                messages.append({"message_id": message.message_id,
                                 "u_id": message.sent_by,
                                 "message": message.content,
                                 "time_created": message.time_sent,
                                 "reacts": reacts,
                                 "is_pinned": message.pinned})

        messages = sorted(messages, key=lambda item: item["time_created"], reverse=True)

        return messages
