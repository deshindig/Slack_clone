""" Contains all the data used on the server that is shared between
    modules.

The data is serialised using Python pickle. This is done to emulate the
behviour of a database. A ServerData class acts as our database, and
contains many extra utilities that deal with the data, decoupling the
application and data layers.

Contains four classes: User, Class, Message, and ServerData. Also contains
methods to load, save, and reset the persistent server data.
"""

import binascii
import copy
import hashlib
import os
import pickle
import random
import re

from server.Error import ValueError

class User():
    """ Class for a user. The u_id is not an attribute of the user object,
        and is instead used to identify the object in a dictionary.
    """

    OWNER_ID = 1
    ADMIN_ID = 2
    USER_ID = 3

    def __init__(self, u_id, email, password, name_first, name_last):
        """ Initialises a user given an email, password, first name, and
            last name. The password is hashed and the permission id is set to
            the user permission my default.
        """

        self.__u_id = u_id
        self.set_email(email)
        self.set_password(password)
        self.set_name_first(name_first)
        self.set_name_last(name_last)
        self.set_permission_id(User.USER_ID)
        self.__handle = ""
        self.__channels = []
        self.__pfp_filename = ""

    def get_id(self):
        """ Returns the user's ID. """

        return self.__u_id

    def set_email(self, email):
        """ Sets a user's email after checking that it is valid. The check for
            if it is already taken is done in auth.
        """

        email_reg_string = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.search(email_reg_string, email):
            self.__email = email
        else:
            raise ValueError("Invalid email")

    def set_handle(self, handle):
        """ Sets a user's handle after checking that it is valid. The check for
            if it is already taken is done in auth.
        """
        if 3 <= len(handle) <= 20:
            self.__handle = handle
        else:
            raise ValueError("Invalid handle")

    def set_name_first(self, name_first):
        """ Sets a user's first name if it is valid. """

        if 1 <= len(name_first) <= 50:
            self.__name_first = name_first
        else:
            raise ValueError("Invalid first name")

    def set_name_last(self, name_last):
        """ Sets a user's last name if it is valid. """

        if 1 <= len(name_last) <= 50:
            self.__name_last = name_last
        else:
            raise ValueError("Invalid last name")

    def set_password(self, password):
        """ Sets a user's password if it is valid.

        The password is stored using a sha256 hash with a salt.
        The salt is generated using the os.urandom() function.
        """

        if len(password) >= 6:
            # generates salt from OS random hashed using sha256
            salt = hashlib.sha256(os.urandom(100))
            salt_bytes = binascii.hexlify(salt.digest())
            # stores salt in hexadecimal form encoded in ascii
            pwd_bytes = password.encode("utf-8")
            # creates binary hash using salt and password
            pwd_hash = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes,
                                           100_000)
            # converts binary hash to hex, then encodes in ascii
            pwd_hash = binascii.hexlify(pwd_hash)
            self.__pwd_hash = (salt_bytes + pwd_hash).decode("ascii")
        else:
            raise ValueError("Invalid password")

    def set_permission_id(self, permission_id):
        """ Sets the permission id (for the Slackr) if it is valid.

        Permission IDs are defined in the User class.
        1 for owner ID, 2 for admin ID, 3 for user ID.
        """
        if permission_id in (1, 2, 3):
            self.__permission_id = permission_id
        else:
            raise ValueError("Invalid permission ID")

    def get_email(self):
        """ Returns the user's email. """

        return self.__email

    def get_handle(self):
        """ Returns the user's handle. """

        return self.__handle

    def get_name_first(self):
        """ Returns the first name of the user. """

        return self.__name_first

    def get_name_last(self):
        """ Returns the last name of the user. """

        return self.__name_last

    def verify_password(self, password_attempt):
        """ Verifies the password attempt against the stored password of the
            user.

        Returns true if the password matches, true if the password does not
        match.
        """

        stored_pwd = self.__pwd_hash
        salt = stored_pwd[:64] # retrieves salt from stored password
        stored_pwd_hash = stored_pwd[64:] # removes the salt from stored password
        salt_bytes = salt.encode("ascii") # encodes salt into bytes in ascii form
        # encodes password attempt into bytes in utf-8 form
        pwd_attempt_bytes = password_attempt.encode("utf-8")
        pwd_attempt_hash = hashlib.pbkdf2_hmac("sha256", pwd_attempt_bytes,
                                               salt_bytes, 100_000)
        pwd_attempt_hash = binascii.hexlify(pwd_attempt_hash).decode("ascii")

        return pwd_attempt_hash == stored_pwd_hash

    def get_permission_id(self):
        """ Returns the permission ID of the user. """

        return self.__permission_id

    def add_channel(self, channel_id):
        """ Adds a channel to the list of channels that the user is in. """

        self.__channels.append(channel_id)

    def remove_channel(self, channel_id):
        """ Removes a channel from the list of channels that the user is in.
        """

        self.__channels.remove(channel_id)

    def get_channels(self):
        """ Gets a copy of the list of channels that the user is in. """

        return self.__channels[:]

    def set_pfp_filename(self, filename):
        """ Sets the user's profile picture filename. """

        self.__pfp_filename = filename

    def get_pfp_filename(self):
        """ Returns the user's profile picture filename. """

        return self.__pfp_filename


class Channel():
    """ Class for a channel. The channel_id is not an attribute of the channel
        object, and is instead used to identify the object in a dictionary.
    """

    def __init__(self, channel_id, creator_id, name, is_public):
        """ Creats a channel given the u_id of the creator, the name of the
            channel, and whether the channel is public.

        Adds the creator to the list of owners and members, and initialises
        the list of messages.
        """

        self.__channel_id = channel_id
        self.__owners = []
        self.__members = []
        self.__messages = []
        self.add_owner(creator_id)
        self.add_member(creator_id)
        self.set_name(name)
        self.set_is_public(is_public)
        self.__current_msg = 0

    def get_id(self):
        """ Returns the channel ID. """

        return self.__channel_id

    def __iter__(self):
        """ The Channel iterator through the message ids in a channel. """
        self.__current_msg = len(self.__messages)
        return self

    def __next__(self):
        """ Returns the next message id in the chnannel. """

        if self.__current_msg <= 0:
            raise StopIteration
        self.__current_msg -= 1
        return self.__messages[self.__current_msg]

    def add_owner(self, owner_id):
        """ Adds an owner to a channel. Assumes the promotee is already a
            member.
        """

        self.__owners.append(owner_id)

    def remove_owner(self, owner_id):
        """ Removes an owner from a channel. Assumes the demotee is a member.
        """

        self.__owners.remove(owner_id)

    def is_owner(self, u_id):
        """ Given a u_id, returns whether or not they are an owner of
            the channel.
        """

        return u_id in self.__owners

    def get_owners(self):
        """ Returns a copy of the list of owners. """

        return self.__owners[:]

    def add_member(self, member_id):
        """ Adds a member to the channel. """

        self.__members.append(member_id)

    def is_member(self, u_id):
        """ Given a u_id, returns whether or not they are a member of
            the channel.
        """

        return u_id in self.__members

    def remove_member(self, member_id):
        """ Removes a member from the list of members given their u_id. Assumes
            that the u_id is a member of the channel.
        """

        self.__members.remove(member_id)

    def get_members(self):
        """ Returns a copy of the list of members. """

        return self.__members[:]

    def add_message(self, message_id):
        """ Adds a message to the channel given its message id. """

        self.__messages.append(message_id)

    def remove_message(self, message_id):
        """ Removes a message from the channel given its message_id. Assumes
            that the message is in the channel.
        """

        self.__messages.remove(message_id)

    def get_messages(self, start, end):
        """ Returns a page of messages in the form of a list of message IDs.
            The page goes from start to end, including start and excluding end.

        When calling this method, always the length of the returned list.
        If less than 50, then you know that you have been returned the last of
        the messages.
        """
        if len(self.__messages) == 0 and start == 0:
            return []
        if start >= len(self.__messages):
            raise ValueError("Start index of message page exceeds number of "
                             "messages in the channel")

        if end < len(self.__messages):
            length = len(self.__messages)
            page = self.__messages[length - start - 1: length - end - 1: -1]
        else:
            length = len(self.__messages)
            page = self.__messages[length - start - 1:: -1]
        return page

    def set_name(self, name):
        """ Sets the name of the channel if it is valid. """

        if len(name) <= 20:
            self.__name = name
        else:
            raise ValueError("Invalid channel name")

    def get_name(self):
        """ Returns the name of the channel. """

        return self.__name

    def set_is_public(self, is_public):
        """ Sets whether the channel is public or private. """

        self.__is_public = is_public

    def is_public(self):
        """ Returns whether the channel is public or private. """

        return self.__is_public


class Message():
    """ Class for a message. The message_id is not an attribute of the message
        object, and is instead used to identify the object in a dictionary.
    """

    def __init__(self, message_id, u_id, channel_id, message, time_sent):
        """ Constructs a method given the poster's user ID, the ID of the
            channel to post in, the body of the message, and the time that
            the message is sent. By default, message is not pinned and has no
            reactions.
        """

        self.__message_id = message_id
        self.set_channel_id(channel_id)
        self.set_message_body(message)
        self.set_u_id(u_id)
        self.set_time_sent(time_sent)
        self.__reacts = {}
        self.__is_pinned = False

    def get_id(self):
        """ Returns the message ID. """

        return self.__message_id

    def set_channel_id(self, channel_id):
        """ Sets the channel_id of the message. """

        self.__channel_id = channel_id

    def get_channel_id(self):
        """ Returns the channel_id of the message. """

        return self.__channel_id

    def set_message_body(self, message):
        """ Sets the body of the message. """

        self.__message_body = message

    def get_message_body(self):
        """ Returns the body of the message. """

        return self.__message_body

    def set_u_id(self, u_id):
        """ Sets the user ID of the user who sent the message. """

        self.__u_id = u_id

    def get_u_id(self):
        """ Returns the user ID of the sender. """

        return self.__u_id

    def set_time_sent(self, time_sent):
        """ Set the time that the message is sent. """

        self.__time_sent = time_sent

    def get_time_sent(self):
        """ Returns the time that the message is sent. """

        return self.__time_sent

    def pin(self):
        """ Pins the message. """

        self.__is_pinned = True

    def unpin(self):
        """ Unpins the message. """

        self.__is_pinned = False

    def is_pinned(self):
        """ Returns whether the message is pinned or not. """

        return self.__is_pinned

    def add_react(self, u_id, react_id):
        """ Adds a react to the message, along with the user ID of the user who
            added the reaction.
        """
        if react_id in self.__reacts:
            raise ValueError("React Id already active")
        self.__reacts[react_id] = [u_id]

    def get_reacts(self):
        """ Returns a copy of all the reactions to the message, along with
            every user who chose that reaction.
        """

        return copy.deepcopy(self.__reacts)

    def remove_react(self, react_id):
        """ Removes a reaction from the message. """

        if react_id not in self.__reacts:
            raise ValueError("React Id already not active")
        del self.__reacts[react_id]


class ServerData():
    """ A ServerData instance contains all the data on a Slackr server. It also
        contains many methods that abstract functionalities regarding the data.
    """

    STATIC_FILEPATH = "static/"
    WORKING_FILEPATH = "working_images/"
    DEFAULT_PFP_FILENAME = "default.jpeg"
    DATA_FILENAME = "data.p"

    def __init__(self):
        """ Constructs a ServerData instance.

        Each object type is given an ID counter, which keeps track of the
        last ID that was registered. This ensures IDs are unique.
        """

        self.__users = {
            # user_id: ###user object###
        }
        self.__channels = {
            # channel_id: ###channel object###
        }
        self.__messages = {
            # message_id: ###message object###
        }
        self.__u_id_counter = 0
        self.__channel_id_counter = 0
        self.__message_id_counter = 0

    def register_user(self, user):
        """ Registers a user object in the server. """

        self.__users[user.get_id()] = user

    def return_user(self, u_id):
        """ Returns a user object given their user ID.

        If the user ID is invalid, raises a ValueError.
        """

        if u_id not in self.__users:
            raise ValueError("Invalid user id")

        return self.__users[u_id]

    def get_all_u_id(self):
        """ Returns a set of all the registered user IDs. """

        return self.__users.keys()

    def register_channel(self, channel):
        """ Registers a channel object in the server. """

        self.__channels[channel.get_id()] = channel

    def return_channel(self, channel_id):
        """ Returns a channel object given its ID.

        If the channel ID is invalid, raises a ValueError.
        """

        if channel_id not in self.__channels:
            raise ValueError("Invalid channel id")

        return self.__channels[channel_id]

    def get_all_channel_id(self):
        """ Returns a set of all the registered channel IDs. """

        return self.__channels.keys()

    def register_message(self, message):
        """ Registers a message object in the server. """

        self.__messages[message.get_id()] = message

    def return_message(self, message_id):
        """ Returns a message object given its ID.

        If the message ID is invalid, raises a ValueError.
        """

        if message_id not in self.__messages:
            raise ValueError("Invalid message id")

        return self.__messages[message_id]

    def delete_message(self, message_id):
        """ Deletes a message from the server given its ID.

        If the message ID is invalid, raises a ValueError.
        """
        # Presently, checking validity of message_id is redundant.
        #if message_id not in self.__messages:
            #raise ValueError("Invalid message id")
        del self.__messages[message_id]

    def get_u_id_counter(self):
        """ Returns the current value of the u_id counter. """

        return self.__u_id_counter

    def get_new_u_id(self):
        """ Returns a new unique user ID. """

        self.__u_id_counter += 1
        return self.__u_id_counter

    def get_new_channel_id(self):
        """ Returns a new unique channel ID. """

        self.__channel_id_counter += 1
        return self.__channel_id_counter

    def get_new_message_id(self):
        """ Returns a new unique message ID. """

        self.__message_id_counter += 1
        return self.__message_id_counter

    def is_registered_email(self, email):
        """ Checks if an email is already in use by another user. """

        for a_user in self.__users.values():
            if email == a_user.get_email():
                return True
        return False

    def is_registered_handle(self, handle):
        """ Checks if a handle is already in use by another user. """

        for a_user in self.__users.values():
            if handle == a_user.get_handle():
                return True
        return False

    def get_u_id_from_email(self, email):
        """ Returns the u_id of a user based on their email.

        If there is no user with that email, raises a ValueError.
        """

        for u_id, user in self.__users.items():
            if email == user.get_email():
                return u_id
        raise ValueError("Unregistered email")

    def generate_unique_handle(self, handle):
        """ Generates a new handle by concatenating a sequence of 3 digits. """

        unique_handle = handle
        i = 0
        while self.is_registered_handle(unique_handle):
            i += 1
            unique_handle = handle
            unique_handle += str(i).rjust(3, "0")

        return unique_handle


def initialise_data():
    """ Resets/sets the server data. All the data is stored in a single
        ServerData object. The data is serialised each time it is modified
        in data.p.
    """

    data = ServerData()
    with open(ServerData.DATA_FILENAME, "wb") as file:
        pickle.dump(data, file)

def load_data():
    """ Loads the data from data.p into a ServerData object. """

    with open(ServerData.DATA_FILENAME, "rb") as file:
        data = pickle.load(file)
    return data

def save_data(data):
    """ Saves the passed server data into data.p. """

    with open(ServerData.DATA_FILENAME, "wb") as file:
        pickle.dump(data, file)
