"""
A file that stores all the data for slackr
"""
import pickle
from error import AccessError, InputError
#pylint: disable=bare-except, invalid-name, global-at-module-level, inconsistent-return-statements, multiple-statements, missing-docstring, undefined-variable
class DataStore:
    """
    All data for a single state/instance of the Slackr app is stored in an
    instance of this object.
    """

    # Data Store Storage Pickle File
    PICKLE_FILE = 'data_store.p'

    def __init__(self):
        self.active_tokens = {}
        self.users = []
        self.channels = []
        self.messages = []
        self.slackr_owner_ids = []
        self.next_id = {}
        self.current_port = None
        self.password_reset_codes = {}

    def update(self):
        """
        Updates the data_store.p file with the contents of the DataStore instance
        """
        with open(self.PICKLE_FILE, "wb") as file:
            pickle.dump(self, file)

    def load(self):
        """
        Loads the DataStore instance in data_store.p
        """
        with open(self.PICKLE_FILE, "rb") as file:
            loaded_data = pickle.load(file)

            self.active_tokens = loaded_data.active_tokens
            self.users = loaded_data.users
            self.channels = loaded_data.channels
            self.messages = loaded_data.messages
            self.slackr_owner_ids = loaded_data.slackr_owner_ids
            self.next_id = loaded_data.next_id


    def setup(self):
        """
        Sets up the data store for the server
        """

        try:
            self.load()
        except:
            self.update()

    def reset(self):
        """
        Resets all fields inside the DataStore object and the
        instance stored in data_store.p
        """
        self.__init__()
        self.update()

    def generate_id(self, object_type):
        """
        Generates an id for a new object to be added to a list in DataStore instance
        """
        result = 1

        if object_type in self.next_id:
            result = self.next_id[object_type]
        else:
            self.next_id[object_type] = result

        self.next_id[object_type] += 1

        return result

    ### Getters ###

    def get_user(self, user_id):
        """
        Returns the User Object using the user ID passed in if found,
        otherwise raises InputError
        """
        for user in self.users:
            if user.user_id == user_id:
                return user

        raise InputError(description="Input error: invalid user ID")

    def get_user_by_email(self, email):
        """
        Returns the User Object using the email passed in if found,
        otherwise returns None
        """
        for user in self.users:
            if user.email == email:
                return user

        return None

    def get_authed_user(self, token, error=True):
        """
        Returns the User ID of the authorised user in active_tokens if they are
        active using a token. Otherwise raises an AccessError
        """
        if token in self.active_tokens:
            return self.get_user(self.active_tokens[token])

        if error:
            raise AccessError(description="Access error: invalid token")

    def get_channel(self, channel_id):
        """
        Returns the Channel Object using the channel ID passed in if found,
        otherwise raises an InputError
        """
        for channel in self.channels:
            if channel.channel_id == channel_id:
                return channel

        raise InputError(description="Input error: invalid channel ID")

    def get_message(self, message_id):
        """
        Returns a Message Object from the data store based on it's id.
        If there is no message with the id, it returns None
        """
        for message in self.messages:
            if message.message_id == message_id:
                return message

        return None

    def add_owner(self, user):
        """
        Assign the user as the owner of slackr.
        """
        if user.user_id not in self.slackr_owner_ids:
            self.slackr_owner_ids.append(user.user_id)

    def remove_owner(self, user):
        """
        Remove the user from being the owner of slackr.
        """
        if user.user_id in self.slackr_owner_ids:
            self.slackr_owner_ids.remove(user.user_id)

    def remove_user(self, user_id):
        user = self.get_user(user_id)

        # Remove all traces of the user from the database
        for message in self.messages:
            if message.sent_by == user_id:
                self.messages.remove(message)

        for channel in self.channels:
            channel.remove_member(user)

        self.remove_owner(user)
        self.users.remove(user)

    ### Data Checking Functions ###

    def email_in_use(self, email):
        """
        Returns True if the email is in use by another user, else False
        """
        if email == "hangman@slackr.com.au": return True
        for user in self.users:
            if user.email == email:
                return True
        return False

    def handle_in_use(self, handle):
        """
        Returns True if the handle is in use by another user, else False
        """
        if handle == "hangman": return True
        for user in self.users:
            if user.handle == handle:
                return True
        return False

### Global Variables ###

#
# These global variables are shared across all files that import this file
#

# Global DataStore object
global database
database = DataStore()
