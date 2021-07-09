'''
A file for the definitions of User
'''
from data_store import database

# pylint: disable=missing-docstring, too-many-arguments, too-many-instance-attributes

class User:
    """
    A User interacting with the Slackr app.
    """

    HANDLE_MAX_LENGTH = 20

    def __init__(self, email, password, name_first, name_last, handle, original_handle):
        # Sets up the new user with their given details
        self.user_id = database.generate_id("user")
        self.password = password
        self.email = email
        self.name_first = name_first
        self.name_last = name_last
        self.handle = handle
        self.original_handle = original_handle
        self.profile_img_url = 'https://iupac.org/wp-content/uploads/2018/05/default-avatar.png'

    def set_handle(self, handle):
        """
        Sets the handle to the given string
        """
        self.handle = handle
        self.original_handle = handle

    def is_owner(self):
        return self.user_id in database.slackr_owner_ids

    def json_member(self):
        return {
            "u_id": self.user_id,
            "name_first": self.name_first,
            "name_last": self.name_last,
            'profile_img_url': self.profile_img_url
        }
